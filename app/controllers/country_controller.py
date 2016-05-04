from flask import g
from sqlalchemy.exc import IntegrityError


# custom exception for country
class CountryException(Exception):
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


class CountryController():

	def __init__(self):
		pass

	def get_countries(self):
		result = g.conn.execute("SELECT DISTINCT ON (c.id) c.*, count(a.id) over (partition by c.id) AS artist_count \
														 FROM countries c \
														 LEFT JOIN artists a ON c.id = a.country_id \
														 GROUP BY c.id, a.id")
		rows = result.fetchall()
		result.close()
		countries = []
		for r in rows:
			countries.append(dict(r))

		return countries

	def get_countries_for_keyword(self, keyword):
		result = g.conn.execute("SELECT DISTINCT ON (c.id) c.*, count(a.id) over (partition by c.id) AS artist_count \
														 FROM countries c \
														 LEFT JOIN artists a ON c.id = a.country_id \
														 WHERE LOWER(c.name) LIKE %s \
														 GROUP BY c.id, a.id", keyword)
		rows = result.fetchall()
		result.close()
		countries = []
		for r in rows:
			countries.append(dict(r))

		return countries

	def get_country(self, country_id):
		result = g.conn.execute("SELECT * FROM countries WHERE id = %s LIMIT 1", country_id)
		country = result.fetchone()
		result.close()
		if not country:
			raise CountryException('country not found', 404)
		return dict(country)

	def create_country(self, name):
		if name == '' or name is None:
			raise CountryException('Country name cannot be blank')

		if len(name) > 50:
			raise CountryException('Country name must be less than 50 characters')

		try:
			result = g.conn.execute("INSERT INTO countries (name) VALUES (%s) RETURNING *", name)
			country = result.fetchone()
			result.close()
			return dict(country)
		except IntegrityError:
			raise CountryException('Country name \"%s\" already exists.' % name)

	def update_country(self, country_id, name):
		if name == '' or name is None:
			raise CountryException('Country name cannot be blank')

		if len(name) > 50:
			raise CountryException('Country name must be less than 50 characters')

		# check if country with given country_id is not in the database
		result = g.conn.execute("SELECT * FROM countries WHERE id=%s LIMIT 1", country_id)
		country = result.fetchone()
		result.close()
		if not country:
			raise CountryException('Country id <%s> not found' % country_id)

		# update country to the database
		try:
			result = g.conn.execute("UPDATE countries SET name=%s WHERE id=%s", name, country_id)
			result.close()
		except IntegrityError:
			raise CountryException('Country name \"%s\" already exists.' % name)

		country = self.get_country(country_id)
		# return the updated country
		return country

	def delete_country(self, country_id):
		result = g.conn.execute("DELETE FROM countries WHERE id=%s", country_id)
		result.close()
		return None
