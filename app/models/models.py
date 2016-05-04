from app import login_manager
from flask import g

class User():

	def __repr__(self):
		return '<Username %r>' % (self.username)

	def __init__(self, id, username, password, first_name, last_name, created_at):
		self.id = id
		self.username = username
		self.password = password
		self.first_name = first_name
		self.last_name = last_name
		self.created_at = created_at

	@login_manager.user_loader
	def load_user(id):
		result = g.conn.execute("SELECT * FROM users WHERE id=%s", id)
		u = result.fetchone()
		user = User(u.id, u.username, u.password, u.first_name, u.last_name, u.created_at)
		result.close()
		return user

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id
