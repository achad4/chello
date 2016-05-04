from app import login_manager
from app.models.models import User
from flask.ext.login import login_user, logout_user
from flask import g
from datetime import date
from dateutil.relativedelta import relativedelta

from sqlalchemy.exc import IntegrityError


# custom exception for authentication
class AuthenticationException(Exception):
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


# custom exception for user controller
class UserControllerException(Exception):
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


class Authentication():

	def __init__(self):
		pass

	def authenticate(self, username, password):
		# check if username and password is given
		if username is None or username == '' or password is None or password == '':
			raise AuthenticationException('Username or password is missing')

		username = username.lower()

		result = g.conn.execute("SELECT * FROM users WHERE username=%s LIMIT 1", username)
		u = result.fetchone()
		result.close()

		if u:
			# check if password is valid
			if u.password == password:
				user = User(u.id, u.username, u.password, u.first_name, u.last_name, u.created_at)
				login_user(user, remember=True)
				return user

			# raise exception if invalid credentials are given
			raise AuthenticationException('Invalid username or password')

		raise AuthenticationException('Username \"%s\" not found' % username) # user not found

	def register(self, username, password, first_name, last_name):
	 	# check if all values are entered
	 	if username is None or username == '' or password is None or password == '' or first_name is None or first_name == '' or last_name is None or last_name == '':
	 		raise AuthenticationException('All fields must be filled out')

	 	if len(username) > 50:
	 		raise AuthenticationException('Username must be less than 50 characters')

	 	if len(first_name) > 50:
	 		raise AuthenticationException('First name must be less than 50 characters')

	 	if len(last_name) > 50:
	 		raise AuthenticationException('Last name must be less than 50 characters')

	 	if not username.isalnum():
	 		raise AuthenticationException('Username can only contain alphanumeric characters')

	 	if len(password) < 6:
	 		raise AuthenticationException('Password must be at least 6 characters')

	 	username = username.lower()
	 	
	 	# add new user to the database
	 	try:
		 	result = g.conn.execute("INSERT INTO users (username, password, first_name, last_name) VALUES (%s,%s,%s,%s)", username, password, first_name, last_name)
			result.close()
		except IntegrityError:
			raise AuthenticationException('Username \"%s\" already exists.' % username)

		result = g.conn.execute("SELECT * FROM users WHERE username=%s LIMIT 1", username)
		u = result.fetchone()
		result.close()

		user = User(u.id, u.username, u.password, u.first_name, u.last_name, u.created_at)

		# create trial user
		user_controller = UserController()
		user_controller._unsubscribe(u.id)
	 	login_user(user, remember=True)

	 	return user

	def logout(self):
		logout_user()
		return True

	def update_account(self, user_id, user):
		username = user.get('username')
		first_name = user.get('first_name')
		last_name = user.get('last_name')

		if username is None or username == '' or first_name is None or first_name == '' or last_name is None or last_name == '':
			raise AuthenticationException('Username, first and last name cannot be blank.')

		if len(username) > 50:
	 		raise AuthenticationException('Username must be less than 50 characters')

	 	if len(first_name) > 50:
	 		raise AuthenticationException('First name must be less than 50 characters')

	 	if len(last_name) > 50:
	 		raise AuthenticationException('Last name must be less than 50 characters')

		if not username.isalnum():
	 		raise AuthenticationException('Username can only contain alphanumeric characters')

		try:
			result = g.conn.execute("UPDATE users SET username=%s, first_name=%s, last_name=%s WHERE id=%s", username, first_name, last_name, user_id)
			result.close()
		except IntegrityError:
			raise AuthenticationException('Username \"%s\" already exists.' % username)

		result = g.conn.execute("SELECT * FROM users WHERE username=%s LIMIT 1", username)
		u = result.fetchone()
		result.close()

		return u

	def update_password(self, user_id, old_pw, new_pw):
		result = g.conn.execute("SELECT * FROM users WHERE id=%s LIMIT 1", user_id)
		u = result.fetchone()
		result.close()

		if u:
			# check if password is valid
			if u.password == old_pw:
				if len(new_pw) < 6:
	 				raise AuthenticationException('Password must be at least 6 characters')

				result = g.conn.execute("UPDATE users SET password=%s WHERE id=%s", new_pw, user_id)
				result.close()
				return u

			raise AuthenticationException('Invalid current password')

		raise AuthenticationException('Invalid user ID') # user not found


class UserController():

	def __init__(self):
		pass

	def get_users(self):
		result = g.conn.execute("WITH ug AS ( \
															SELECT DISTINCT u.*, count(follower.following_id) as follower_count \
															FROM users u \
															LEFT JOIN follows follower ON follower.following_id = u.id \
															GROUP BY u.id, follower.following_id \
														) \
														SELECT ug.*, count(following.follower_id) as following_count \
														FROM ug \
														LEFT JOIN follows following ON following.follower_id = ug.id \
														GROUP BY ug.id, ug.username, ug.first_name, ug.last_name, ug.password, ug.created_at, ug.follower_count, following.follower_id")
		rows = result.fetchall()
		result.close()

		users = []

		for r in rows:
			users.append(dict(r))

		return users

	def get_user(self, user_id):
		result = g.conn.execute("WITH ug AS ( \
															SELECT DISTINCT u.*, count(follower.following_id) as follower_count \
															FROM users u \
															LEFT JOIN follows follower ON follower.following_id = u.id \
															WHERE u.id = %s \
															GROUP BY u.id, follower.following_id \
														) \
														SELECT ug.*, count(following.follower_id) as following_count \
														FROM ug \
														LEFT JOIN follows following ON following.follower_id = ug.id \
														GROUP BY ug.id, ug.username, ug.first_name, ug.last_name, ug.password, ug.created_at, ug.follower_count, following.follower_id \
														LIMIT 1", user_id)
		user = result.fetchone()
		result.close()
		if not user:
			raise UserControllerException('user not found', 404)
		return dict(user)

	def get_users_by_keyword(self, keyword):
		# result = g.conn.execute("SELECT * FROM users WHERE username LIKE %s OR first_name LIKE %s OR last_name LIKE %s LIMIT 50", keyword, keyword, keyword)
		result = g.conn.execute("WITH ug AS ( \
															SELECT DISTINCT u.*, count(follower.following_id) as follower_count \
															FROM users u \
															LEFT JOIN follows follower ON follower.following_id = u.id \
															WHERE LOWER(u.username) LIKE %s OR LOWER(u.first_name) LIKE %s OR LOWER(u.last_name) LIKE %s \
															GROUP BY u.id, follower.following_id \
														) \
														SELECT ug.*, count(following.follower_id) as following_count \
														FROM ug \
														LEFT JOIN follows following ON following.follower_id = ug.id \
														GROUP BY ug.id, ug.username, ug.first_name, ug.last_name, ug.password, ug.created_at, ug.follower_count, following.follower_id", keyword, keyword, keyword)
		rows = result.fetchall()
		result.close()

		users = []

		for r in rows:
			users.append(dict(r))

		return users

	# get list of followers of user
	def get_followers(self, user_id):
		result = g.conn.execute("WITH ug AS ( \
															SELECT DISTINCT u.*, count(follower.following_id) as follower_count \
															FROM users u \
															LEFT JOIN follows follower ON follower.following_id = u.id \
															GROUP BY u.id, follower.following_id \
														) \
														SELECT ug.*, count(following.follower_id) as following_count \
														FROM ug \
														LEFT JOIN follows following ON following.follower_id = ug.id \
														WHERE following.following_id = %s \
														GROUP BY ug.id, ug.username, ug.first_name, ug.last_name, ug.password, ug.created_at, ug.follower_count, following.follower_id", user_id)
		rows = result.fetchall()
		result.close()

		users = []

		for r in rows:
			users.append(dict(r))

		return users

	# get list of users that this user follows
	def get_following_users(self, user_id):
		result = g.conn.execute("WITH ug AS ( \
															SELECT DISTINCT u.*, count(follower.following_id) as follower_count \
															FROM users u \
															LEFT JOIN follows follower ON follower.following_id = u.id \
															WHERE follower.follower_id = %s \
															GROUP BY u.id, follower.following_id \
														) \
														SELECT ug.*, count(following.follower_id) as following_count \
														FROM ug \
														LEFT JOIN follows following ON following.follower_id = ug.id \
														GROUP BY ug.id, ug.username, ug.first_name, ug.last_name, ug.password, ug.created_at, ug.follower_count, following.follower_id", user_id)
		rows = result.fetchall()
		result.close()

		users = []

		for r in rows:
			users.append(dict(r))

		return users

	def follow_user(self, user_id, following_id):
		if user_id == following_id:
			raise UserControllerException('User <%s> cannot follows oneself' % user_id)

		result = g.conn.execute("SELECT * FROM follows WHERE follower_id = %s AND following_id = %s LIMIT 1", user_id, following_id)
		follows = result.fetchone()
		result.close()
		
		if follows:
			raise UserControllerException('User <%s> already follows user <%s> found' % (user_id, following_id))

		result = g.conn.execute("INSERT INTO follows (follower_id, following_id) VALUES (%s, %s)", user_id, following_id)
		result.close()

		return False

	def unfollow_user(self, user_id, following_id):
		if user_id == following_id:
			raise UserControllerException('User <%s> cannot unfollow oneself' % user_id)

		result = g.conn.execute("SELECT * FROM follows WHERE follower_id = %s AND following_id = %s LIMIT 1", user_id, following_id)
		follows = result.fetchone()
		result.close()
		
		if not follows:
			raise UserControllerException('User <%s> is not following user <%s> found' % (user_id, following_id))

		result = g.conn.execute("DELETE FROM follows WHERE follower_id = %s AND following_id = %s", user_id, following_id)
		result.close()

		return True

	def is_following(self, user_id, following_id):
		result = g.conn.execute("SELECT * FROM follows WHERE follower_id = %s AND following_id = %s LIMIT 1", user_id, following_id)
		follows = result.fetchone()
		result.close()
		return True if follows else False

	def get_subscription(self, user_id):
		result = g.conn.execute("SELECT * FROM subscribed_users WHERE user_id = %s LIMIT 1", user_id)
		subscribed = result.fetchone()
		result.close()

		if subscribed and subscribed.effective_until >= date.today():
			return dict({'subscribed': True, 'effective_until': subscribed.effective_until})
		elif subscribed:
			# unsubscribe if date is not effective
			return self._unsubscribe(user_id)

		result = g.conn.execute("SELECT * FROM trial_users WHERE user_id = %s LIMIT 1", user_id)
		trial = result.fetchone()
		result.close()

		if not trial:
			return self._unsubscribe(user_id)

		return dict({'subscribed': False, 'remaining_playcount': trial.remaining_playcount})

	def update_subscription(self, user_id, subscribe_option):
		result = g.conn.execute("SELECT * FROM subscribed_users WHERE user_id = %s LIMIT 1", user_id)
		subscribed = result.fetchone()
		result.close()

		if subscribe_option == False:
			if not subscribed:
				raise UserControllerException('User <%s> is already unsubscribed' % user_id)
			return self._unsubscribe(user_id)

		return self._subscribe(user_id)

	def _unsubscribe(self, user_id):
		result = g.conn.execute("DELETE FROM subscribed_users WHERE user_id=%s", user_id)
		result.close()
		result = g.conn.execute("INSERT INTO trial_users (user_id) VALUES (%s) RETURNING *", user_id)
		trial = result.fetchone()
		result.close()
		return dict({'subscribed': False, 'remaining_playcount': trial.remaining_playcount})

	def _subscribe(self, user_id):
		today = date.today()
		result = g.conn.execute("DELETE FROM trial_users WHERE user_id=%s", user_id)
		result.close()
		new_date = today + relativedelta(years=1)
		result = g.conn.execute("INSERT INTO subscribed_users (user_id, effective_until) VALUES (%s, %s) RETURNING *", user_id, new_date)
		subscribed = result.fetchone()
		result.close()
		return dict({'subscribed': True, 'effective_until': subscribed.effective_until})

	def decrement_count(self, user_id):
		subscription = self.get_subscription(user_id)

		# no need to decrement if subscribed
		if subscription['subscribed']:
			return 50

		new_count = subscription['remaining_playcount'] - 1

		if new_count < 0:
			raise UserControllerException('User <%s> used up all play counts' % user_id)
		result = g.conn.execute("UPDATE trial_users SET remaining_playcount=%s WHERE user_id=%s", new_count, user_id)
		return new_count

@login_manager.user_loader
def user_loader(user_id):
  result = g.conn.execute("SELECT * FROM users WHERE id=%s", user_id)
  u = result.fetchone()
  user = User(u.id, u.username, u.password, u.first_name, u.last_name, u.created_at)
  result.close()
  return user