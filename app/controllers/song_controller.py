from flask import g
from app.controllers.artist_controller import ArtistController
# from app.controllers.genre_controller import GenreController
from app.controllers.album_controller import AlbumController

from sqlalchemy.exc import IntegrityError

artist_controller = ArtistController()
# genre_controller = GenreController()
album_controller = AlbumController()


# custom exception for song
class SongException(Exception):
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


class SongController():

	def __init__(self):
		pass

	def get_songs_for_playlist(self, playlist_id):
		# get list of songs for a playlist
		result = g.conn.execute("SELECT DISTINCT ON (s.id) s.*, b.id as album_id, b.title as album_title \
														 FROM songs s \
														 LEFT JOIN playlist_contains pc ON s.id = pc.song_id \
														 LEFT JOIN album_contains ac ON s.id = ac.song_id \
														 LEFT JOIN albums b ON b.id = ac.album_id \
														 WHERE pc.playlist_id=%s", playlist_id)
		rows = result.fetchall()
		result.close()
		songs = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_song(r.id)
			songs.append(r_dict)

		return songs

	def get_songs_for_album(self, album_id):
		# get list of songs for a playlist
		result = g.conn.execute("SELECT s.* FROM songs s \
														 LEFT JOIN album_contains ac ON s.id = ac.song_id \
														 WHERE ac.album_id=%s", album_id)
		rows = result.fetchall()
		result.close()
		songs = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_song(r.id)
			# r_dict['genres'] = genre_controller.get_genres_for_song(r.id)
			songs.append(r_dict)

		return songs

	def get_songs_for_genre(self, genre_id):
		# get list of songs for a genre
		result = g.conn.execute("SELECT s.* FROM songs s \
														 LEFT JOIN song_categorized_in sc ON s.id = sc.song_id \
														 WHERE sc.genre_id=%s", genre_id)
		rows = result.fetchall()
		result.close()
		songs = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_song(r.id)
			songs.append(r_dict)

		return songs

	def get_songs(self):
		# get list of songs
		result = g.conn.execute("SELECT s.* FROM songs s")
		rows = result.fetchall()
		result.close()
		songs = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_song(r.id)
			# r_dict['genres'] = genre_controller.get_genres_for_song(r.id)
			songs.append(r_dict)

		return songs

	def get_songs_for_keyword(self, keyword):
		result = g.conn.execute("SELECT s.* FROM songs s WHERE LOWER(s.title) LIKE %s", keyword)
		rows = result.fetchall()
		result.close()
		songs = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_song(r.id)
			# r_dict['genres'] = genre_controller.get_genres_for_song(r.id)
			songs.append(r_dict)

		return songs

	def get_songs_for_select(self):
		# get list of songs
		result = g.conn.execute("SELECT s.* FROM songs s")
		rows = result.fetchall()
		result.close()
		songs = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_song(r.id)
			songs.append(r_dict)

		return songs

	def get_song(self, song_id):
		result = g.conn.execute("SELECT s.* FROM songs s \
														 WHERE s.id = %s ", song_id)
		r = result.fetchone()
		result.close()
		if not r:
			raise SongException('song not found', 404)
		song = dict(r)
		song['album'] = album_controller.get_albums_for_song(song_id)
		song['artists'] = artist_controller.get_artists_for_song(song_id)
		# song['genres'] = genre_controller.get_genres_for_song(song_id)
		return song

	def create_song(self, title, duration, url, source, source_id, thumbnail, album_id, genre_ids):
		if title == '' or title is None:
			raise SongException('Song title cannot be blank')

		if len(title) > 50:
			raise SongException('Song title must be less than 50 characters')

		if url == '' or url is None or source == '' or source is None or source_id == '' or source_id is None:
			raise SongException('Song url, source, and source ID cannot be blank')

		if duration < 0:
			raise SongException('Song duration must be greater than 0')

		if len(thumbnail) > 400:
			raise SongException('Song thumbnail URL must be less than 400 characters')

		if not album_id or album_id == '':
			raise SongException('Album cannot be blank')

		try:
			result = g.conn.execute("INSERT INTO songs (title, duration, url, source, source_id, thumbnail) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *", title, duration, url, source, source_id, thumbnail)
			song = result.fetchone()
			result.close()
		except IntegrityError:
			raise SongException('Song url <%s> is already added' % url)

		try:
			result = g.conn.execute("INSERT INTO album_contains (album_id, song_id) VALUES (%s, %s)", album_id, song.id)
			result.close()
		except IntegrityError:
			self.delete_song(song.id)
			raise SongException('Album with id <%s> not found.' % album_id)

		for g_id in genre_ids:
			try:
				result = g.conn.execute("INSERT INTO song_categorized_in (genre_id, song_id) VALUES (%s, %s)", g_id, song.id)
				result.close()
			except IntegrityError:
				self.delete_song(song.id)
				raise SongException('Genre with id <%s> not found.' % g_id)

		return dict(song)

	def update_song(self, song_id, title, duration, url, source, source_id, thumbnail, album_id, genre_ids):
		if title == '' or title is None:
			raise SongException('Song title cannot be blank')

		if len(title) > 50:
			raise SongException('Song title must be less than 50 characters')

		if url == '' or url is None or source == '' or source is None or source_id == '' or source_id is None:
			raise SongException('Song url, source, and source ID cannot be blank')

		if duration < 0:
			raise SongException('Song duration must be greater than 0')

		if len(thumbnail) > 400:
			raise SongException('Song thumbnail URL must be less than 400 characters')

		if not album_id or album_id == '':
			raise SongException('Album cannot be blank')

		# check if song with given song_id is not in the database
		result = g.conn.execute("SELECT * FROM songs WHERE id=%s LIMIT 1", song_id)
		song = result.fetchone()
		result.close()
		if not song:
			raise SongException('Song id <%s> not found' % song_id)

		result = g.conn.execute("SELECT * FROM song_categorized_in WHERE song_id=%s", song_id)
		sc = result.fetchall()
		original_genres = [a.genre_id for a in sc]
		result.close()
		deleted_genres = list(set(original_genres) - set(genre_ids))
		added_genres = list(set(genre_ids) - set(original_genres))

		# update song to the database
		try:
			result = g.conn.execute("UPDATE songs \
															 SET title=%s, duration=%s, url=%s, source=%s, source_id=%s, thumbnail=%s \
															 WHERE id=%s",
															 title, duration, url, source, source_id, thumbnail, song_id)
			result.close()
		except IntegrityError:
			raise SongException('Song url <%s> is already added' % url)

		# add relations
		try:
			result = g.conn.execute("UPDATE album_contains SET album_id=%s WHERE song_id=%s", album_id, song_id)
			result.close()
		except IntegrityError:
			pass

		for g_id in added_genres:
			try:
				result = g.conn.execute("INSERT INTO song_categorized_in (genre_id, song_id) VALUES (%s, %s)", g_id, song_id)
				result.close()
			except IntegrityError:
				pass

		for g_id in deleted_genres:
			result = g.conn.execute("DELETE FROM song_categorized_in WHERE genre_id=%s AND song_id=%s", g_id, song_id)
			result.close()

		return dict(song)

	def delete_song(self, song_id):
		result = g.conn.execute("DELETE FROM songs WHERE id=%s", song_id)
		result.close()
		return None
