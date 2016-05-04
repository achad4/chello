from flask import g
from sqlalchemy.exc import IntegrityError

# custom exception for playlist
class PlaylistException(Exception):
	status_code = 400

	def __init__(self, message, status_code=None, payload=None):
		Exception.__init__(self)
		self.message = message
		if status_code is not None:
			self.status_code = status_code
		self.payload = payload

	def to_dict(self):
		rv = dict(self.payload or ())
		rv['message'] = self.message
		return rv


class PlaylistController():

	def __init__(self):
		pass

	def get_public_playlists(self):
		# get list of playlists that are public, its song count as well as thumnail of one of the songs in the playlist
		result = g.conn.execute("SELECT DISTINCT ON (p.id) p.*, s.thumbnail AS thumbnail, count(s.id) over (partition by p.id) AS song_count, u.username, u.first_name, u.last_name \
														 FROM playlists p \
														 LEFT JOIN playlist_contains pc ON p.id = pc.playlist_id \
														 LEFT JOIN songs s on s.id = pc.song_id \
														 LEFT JOIN users u on u.id = p.user_id \
														 WHERE p.is_public=TRUE GROUP BY p.id, s.thumbnail, s.id, u.username, u.first_name, u.last_name")
		rows = result.fetchall()
		result.close()
		playlists = []
		for r in rows:
			playlists.append(dict(r))

		return playlists

	def get_public_playlists_for_keyword(self, keyword):
		result = g.conn.execute("SELECT DISTINCT ON (p.id) p.*, s.thumbnail AS thumbnail, count(s.id) over (partition by p.id) AS song_count, u.username, u.first_name, u.last_name \
														 FROM playlists p \
														 LEFT JOIN playlist_contains pc ON p.id = pc.playlist_id \
														 LEFT JOIN songs s on s.id = pc.song_id \
														 LEFT JOIN users u on u.id = p.user_id \
														 WHERE p.is_public=TRUE AND LOWER(p.name) LIKE %s GROUP BY p.id, s.thumbnail, s.id, u.username, u.first_name, u.last_name", keyword)
		rows = result.fetchall()
		result.close()
		playlists = []
		for r in rows:
			playlists.append(dict(r))

		return playlists

	def get_playlists_for_user(self, user_id, is_current_user):
		# get list of playlists for a user, its song count as well as thumnail of one of the songs in the playlist
		if is_current_user:
			result = g.conn.execute("SELECT DISTINCT ON (p.id) p.*, s.thumbnail AS thumbnail, count(s.id) over (partition by p.id) AS song_count, u.username, u.first_name, u.last_name \
															 FROM playlists p \
															 LEFT JOIN playlist_contains pc ON p.id = pc.playlist_id \
															 LEFT JOIN songs s on s.id = pc.song_id \
															 LEFT JOIN users u on u.id = p.user_id \
															 WHERE p.user_id=%s GROUP BY p.id, s.thumbnail, s.id, u.username, u.first_name, u.last_name", user_id)
		else:
			result = g.conn.execute("SELECT DISTINCT ON (p.id) p.*, s.thumbnail AS thumbnail, count(s.id) over (partition by p.id) AS song_count, u.username, u.first_name, u.last_name \
															 FROM playlists p \
															 LEFT JOIN playlist_contains pc ON p.id = pc.playlist_id \
															 LEFT JOIN songs s on s.id = pc.song_id \
															 LEFT JOIN users u on u.id = p.user_id \
															 WHERE p.user_id=%s AND p.is_public=TRUE GROUP BY p.id, s.thumbnail, s.id, u.username, u.first_name, u.last_name", user_id)

		rows = result.fetchall()
		result.close()
		playlists = []
		for r in rows:
			playlists.append(dict(r))

		return playlists

	def get_playlist(self, playlist_id):
		result = g.conn.execute("SELECT p.*, u.username, u.first_name, u.last_name FROM playlists p LEFT JOIN users u on u.id = p.user_id WHERE p.id=%s", playlist_id)
		playlist = result.fetchone()
		if not playlist:
			raise PlaylistException('not found', 404)
		result.close()
		return dict(playlist)

	def create_playlist(self, user_id, name, is_public):
		if name == '' or name is None:
			raise PlaylistException('Playlist name cannot be blank')

		if len(name) > 50:
			raise PlaylistException('Playlist name must be less than 50 characters')

		if is_public == '' or is_public is None:
			is_public = False

		result = g.conn.execute("INSERT INTO playlists (user_id, name, is_public) VALUES (%s, %s, %s) RETURNING *", user_id, name, is_public)
		playlist = result.fetchone()
		result.close()
		return dict(playlist)

	def update_playlist(self, user_id, playlist_id, name, is_public):
		if name == '' or name is None:
			raise PlaylistException('Playlist name cannot be blank')

		if len(name) > 50:
			raise PlaylistException('Playlist name must be less than 50 characters')

		if is_public == '' or is_public is None:
			is_public = False

		# check if playlist with given playlist_id is not in the database
		result = g.conn.execute("SELECT * FROM playlists WHERE user_id=%s AND id=%s", user_id, playlist_id)
		playlist = result.fetchone()
		result.close()

		if not playlist:
			raise PlaylistException('Playlist id <%s> not found' % playlist_id)

		# update playlist to the database
		result = g.conn.execute("UPDATE playlists SET name=%s, is_public=%s WHERE id=%s", name, is_public, playlist_id)
		result.close()

		# fetch updated playlist with songs
		playlist = self.get_playlist(playlist_id)

		# return the updated playlist
		return playlist

	def delete_playlist(self, user_id, playlist_id):
		result = g.conn.execute("DELETE FROM playlists WHERE id=%s AND user_id=%s", playlist_id, user_id)
		result.close()

		return None

	def verify_playlist_owner(self, user_id, playlist_id):
		result = g.conn.execute("SELECT * FROM playlists WHERE user_id=%s", user_id)
		playlist = result.fetchone()
		result.close()

		# if playlist is not found, return False
		if not playlist:
			return False

		# if playlist user ID matches the current user's id, return True
		if playlist.user_id == user_id:
			return True

		# else, return False
		return False

	def add_songs_to_playlist(self, user_id, playlist_id, song_ids):
		result = g.conn.execute("SELECT * FROM playlists WHERE id=%s", playlist_id)
		playlist = result.fetchone()
		result.close()

		not_added = False

		if not playlist:
			raise PlaylistException('Playlist not found')

		# check if user is the owner
		if playlist.user_id != user_id:
			raise PlaylistException('User id <%s> not the owner of playlist <%s>' % (user_id, playlist_id))

		# add relations
		for song_id in song_ids:
			try:
				result = g.conn.execute("INSERT INTO playlist_contains (song_id, playlist_id) VALUES (%s, %s)", song_id, playlist_id)
				result.close()
			except IntegrityError:
				not_added = True

		playlist = self.get_playlist(playlist_id)
		playlist['not_added'] = not_added

		return playlist

	def delete_song_from_playlist(self, user_id, playlist_id, song_id):
		result = g.conn.execute("SELECT * FROM playlists WHERE id=%s", playlist_id)
		playlist = result.fetchone()
		result.close()

		if not playlist:
			raise PlaylistException('Playlist not found')

		# check if user is the owner
		if playlist.user_id != user_id:
			raise PlaylistException('User id <%s> not the owner of playlist <%s>' % (user_id, playlist_id))

		result = g.conn.execute("DELETE FROM playlist_contains WHERE song_id=%s AND playlist_id=%s", song_id, playlist_id)
		result.close()

		return None
