from flask import g
from sqlalchemy.exc import IntegrityError

from app.controllers.artist_controller import ArtistController
from app.controllers.genre_controller import GenreController

artist_controller = ArtistController()
genre_controller = GenreController()


# custom exception for album
class AlbumException(Exception):
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


class AlbumController():

	def __init__(self):
		pass

	def get_albums_for_artist(self, artist_id):
		result = g.conn.execute("SELECT DISTINCT ON (b.id) b.*, s.thumbnail as thumbnail, count(ac.song_id) over (partition by b.id) AS song_count \
														 FROM albums b \
														 LEFT JOIN album_performed_by ap ON ap.album_id = b.id \
														 LEFT JOIN album_contains ac ON ac.album_id = b.id \
														 LEFT JOIN songs s on s.id = ac.song_id \
														 WHERE ap.artist_id = %s \
														 GROUP BY b.id, s.thumbnail, ac.song_id", artist_id)

		rows = result.fetchall()
		result.close()
		albums = []
		for r in rows:
			r_dict = dict(r)
			r_dict['genres'] = genre_controller.get_genres_for_album(r.id)
			albums.append(r_dict)
		return albums

	def get_albums_for_song(self, song_id):
		result = g.conn.execute("SELECT b.* \
														 FROM albums b, album_contains ac \
														 WHERE ac.song_id = %s AND ac.album_id = b.id", song_id)
		album = result.fetchone()
		result.close()
		# albums = []
		# for r in rows:
		# 	r_dict = dict(r)
		# 	albums.append(r_dict)
		return dict(album)

	def get_albums_for_genre(self, genre_id):
		result = g.conn.execute("SELECT DISTINCT ON (b.id) b.*, s.thumbnail as thumbnail, count(ac.song_id) over (partition by b.id) AS song_count \
														 FROM albums b \
														 LEFT JOIN album_categorized_in ap ON ap.album_id = b.id \
														 LEFT JOIN album_contains ac ON ac.album_id = b.id \
														 LEFT JOIN songs s on s.id = ac.song_id \
														 WHERE ap.genre_id = %s \
														 GROUP BY b.id, s.thumbnail, ac.song_id", genre_id)

		rows = result.fetchall()
		result.close()
		albums = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_album(r.id)
			albums.append(r_dict)
		return albums

	def get_albums(self):
		result = g.conn.execute("SELECT DISTINCT ON (b.id) b.*, s.thumbnail as thumbnail, count(ac.song_id) over (partition by b.id) AS song_count \
														 FROM albums b \
														 LEFT JOIN album_contains ac ON ac.album_id = b.id \
														 LEFT JOIN songs s on s.id = ac.song_id \
														 GROUP BY b.id, s.thumbnail, ac.song_id")

		rows = result.fetchall()
		result.close()
		albums = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_album(r.id)
			r_dict['genres'] = genre_controller.get_genres_for_album(r.id)
			albums.append(r_dict)
		return albums

	def get_albums_for_keyword(self, keyword):
		result = g.conn.execute("SELECT DISTINCT ON (b.id) b.*, s.thumbnail as thumbnail, count(ac.song_id) over (partition by b.id) AS song_count \
														 FROM albums b \
														 LEFT JOIN album_contains ac ON ac.album_id = b.id \
														 LEFT JOIN songs s on s.id = ac.song_id \
														 WHERE LOWER(b.title) LIKE %s \
														 GROUP BY b.id, s.thumbnail, ac.song_id", keyword)

		rows = result.fetchall()
		result.close()
		albums = []
		for r in rows:
			r_dict = dict(r)
			r_dict['artists'] = artist_controller.get_artists_for_album(r.id)
			r_dict['genres'] = genre_controller.get_genres_for_album(r.id)
			albums.append(r_dict)
		return albums

	def get_album(self, album_id):
		result = g.conn.execute("SELECT b.* \
														 FROM albums b \
														 WHERE b.id = %s LIMIT 1", album_id)
		r = result.fetchone()
		result.close()
		if not r:
			raise AlbumException('album not found', 404)
		album = dict(r)
		# album['artists'] = artist_controller.get_artists_for_album(r.id)
		# album['songs'] = song_controller.get_songs_for_album(r.id)
		return album

	def create_album(self, title, release_date, artist_ids, genre_ids):
		if title == '' or title is None:
			raise AlbumException('Album title cannot be blank')

		if len(title) > 50:
			raise AlbumException('Album title must be less than 50 characters')

		if release_date == '':
			release_date = None

		result = g.conn.execute("INSERT INTO albums (title, release_date) VALUES (%s, %s) RETURNING *", title, release_date)
		album = result.fetchone()
		result.close()

		for a_id in artist_ids:
			try:
				result = g.conn.execute("INSERT INTO album_performed_by (artist_id, album_id) VALUES (%s, %s) RETURNING *", a_id, album.id)
				result.close()
			except IntegrityError:
				self.delete_album(album.id)
				raise AlbumException('Artist with id <%s> not found.' % a_id)

		for g_id in genre_ids:
			try:
				result = g.conn.execute("INSERT INTO album_categorized_in (genre_id, album_id) VALUES (%s, %s) RETURNING *", g_id, album.id)
				result.close()
			except IntegrityError:
				self.delete_album(album.id)
				raise AlbumException('Genre with id <%s> not found.' % g_id)

		return dict(album)

	def update_album(self, album_id, title, release_date, artist_ids, genre_ids):
		if title == '' or title is None:
			raise AlbumException('Album title cannot be blank')

		if len(title) > 50:
			raise AlbumException('Album title must be less than 50 characters')

		if release_date == '':
			release_date = None

		# check if album with given album_id is not in the database
		result = g.conn.execute("SELECT * FROM albums WHERE id=%s LIMIT 1", album_id)
		album = result.fetchone()
		result.close()
		if not album:
			raise AlbumException('Album id <%s> not found' % album_id)

		result = g.conn.execute("SELECT * FROM album_performed_by WHERE album_id=%s", album_id)
		ap = result.fetchall()
		original_artists = [a.artist_id for a in ap]
		result.close()
		result = g.conn.execute("SELECT * FROM album_categorized_in WHERE album_id=%s", album_id)
		ac = result.fetchall()
		original_genres = [a.genre_id for a in ac]
		result.close()
		deleted_artists = list(set(original_artists) - set(artist_ids))
		deleted_genres = list(set(original_genres) - set(genre_ids))
		added_artists = list(set(artist_ids) - set(original_artists))
		added_genres = list(set(genre_ids) - set(original_genres))

		# update album to the database
		result = g.conn.execute("UPDATE albums SET title=%s, release_date=%s WHERE id=%s", title, release_date, album_id)
		result.close()

		# add relations
		for a_id in added_artists:
			try:
				result = g.conn.execute("INSERT INTO album_performed_by (artist_id, album_id) VALUES (%s, %s) RETURNING *", a_id, album_id)
				result.close()
			except IntegrityError:
				pass

		for g_id in added_genres:
			try:
				result = g.conn.execute("INSERT INTO album_categorized_in (genre_id, album_id) VALUES (%s, %s) RETURNING *", g_id, album_id)
				result.close()
			except IntegrityError:
				pass

		# delete relations
		for a_id in deleted_artists:
			result = g.conn.execute("DELETE FROM album_performed_by WHERE artist_id=%s AND album_id=%s", a_id, album_id)
			result.close()

		for g_id in deleted_genres:
			result = g.conn.execute("DELETE FROM album_categorized_in WHERE genre_id=%s AND album_id=%s", g_id, album_id)
			result.close()

		return dict(album)


	def delete_album(self, album_id):
		result = g.conn.execute("DELETE FROM albums WHERE id=%s", album_id)
		result.close()
		return None
