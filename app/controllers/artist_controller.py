from flask import g
from sqlalchemy.exc import IntegrityError


# custom exception for artist
class ArtistException(Exception):
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


class ArtistController():

	def __init__(self):
		pass

	def get_artists_for_country(self, country_id):
		result = g.conn.execute("SELECT DISTINCT ON (a.id) a.*, count(ap.album_id) over (partition by a.id) AS album_count \
															 FROM artists a \
															 LEFT JOIN album_performed_by ap ON ap.artist_id = a.id \
															 WHERE a.country_id = %s GROUP BY a.id, ap.album_id", country_id)

		rows = result.fetchall()
		result.close()
		artists = []
		for r in rows:
			artists.append(dict(r))

		return artists

	def get_artists_for_album(self, album_id):
		result = g.conn.execute("SELECT DISTINCT ON (a.id) a.* \
															 FROM artists a \
															 LEFT JOIN album_performed_by ap ON ap.artist_id = a.id \
															 WHERE ap.album_id = %s GROUP BY a.id", album_id)

		rows = result.fetchall()
		result.close()
		artists = []
		for r in rows:
			artists.append(dict(r))

		return artists

	def get_artists_for_song(self, song_id):
		result = g.conn.execute("SELECT DISTINCT ON (a.id) a.* \
															 FROM artists a \
															 LEFT JOIN album_performed_by ap ON ap.artist_id = a.id \
															 LEFT JOIN album_contains ac ON ac.album_id = ap.album_id \
															 WHERE ac.song_id = %s GROUP BY a.id", song_id)

		rows = result.fetchall()
		result.close()
		artists = []
		for r in rows:
			artists.append(dict(r))

		return artists

	def get_artists(self):
		result = g.conn.execute("SELECT DISTINCT ON (a.id) a.*, count(ap.album_id) over (partition by a.id) AS album_count \
															 FROM artists a \
															 LEFT JOIN album_performed_by ap ON ap.artist_id = a.id \
															 GROUP BY a.id, ap.album_id")

		rows = result.fetchall()
		result.close()
		artists = []
		for r in rows:
			artists.append(dict(r))

		return artists

	def get_artists_for_keyword(self, keyword):
		result = g.conn.execute("SELECT DISTINCT ON (a.id) a.*, count(ap.album_id) over (partition by a.id) AS album_count \
															 FROM artists a \
															 LEFT JOIN album_performed_by ap ON ap.artist_id = a.id \
															 WHERE LOWER(a.name) LIKE %s \
															 GROUP BY a.id, ap.album_id", keyword)

		rows = result.fetchall()
		result.close()
		artists = []
		for r in rows:
			artists.append(dict(r))

		return artists

	def get_artist(self, artist_id):
		result = g.conn.execute("SELECT a.*, c.name as country_name \
														 FROM artists a \
														 LEFT JOIN countries c ON c.id = a.country_id \
														 WHERE a.id = %s LIMIT 1", artist_id)
		r = result.fetchone()
		result.close()
		if not r:
			raise ArtistException('artist not found', 404)
		return dict(r)

	def create_artist(self, name, country_id):
		if name == '' or name is None or country_id == '' or country_id is None:
			raise ArtistException('Artist name and country cannot be blank')

		if len(name) > 50:
			raise ArtistException('Artist name must be less than 50 characters')

		try:
			result = g.conn.execute("INSERT INTO artists (name, country_id) VALUES (%s, %s) RETURNING *", name, country_id)
			artist = result.fetchone()
			result.close()
			return dict(artist)
		except IntegrityError:
			raise ArtistException('Country with id <%s> not found.' % country_id)

	def update_artist(self, artist_id, name, country_id):
		if name == '' or name is None or country_id == '' or country_id is None:
			raise ArtistException('Artist name and country cannot be blank')

		if len(name) > 50:
			raise ArtistException('Artist name must be less than 50 characters')

		# check if artist with given artist_id is not in the database
		result = g.conn.execute("SELECT * FROM artists WHERE id=%s LIMIT 1", artist_id)
		artist = result.fetchone()
		result.close()
		if not artist:
			raise ArtistException('Artist id <%s> not found' % artist_id)

		# update artist to the database
		try:
			result = g.conn.execute("UPDATE artists SET name=%s, country_id=%s WHERE id=%s RETURNING *", name, country_id, artist_id)
			artist = result.fetchone()
			result.close()
			return dict(artist)

		except IntegrityError:
			raise ArtistException('Country with id <%s> not found.' % country_id)


	def delete_artist(self, artist_id):
		result = g.conn.execute("DELETE FROM artists WHERE id=%s", artist_id)
		result.close()
		return None
