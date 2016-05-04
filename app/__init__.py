#!/usr/bin/env python2.7


import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, jsonify
import os
from flask.ext.login import LoginManager, login_required, current_user

import json

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), './static')

# set asset directory for templates and static files
app = Flask(__name__, static_url_path='', template_folder=ASSET_DIR, static_folder=ASSET_DIR)
app.config.from_object('config')
login_manager = LoginManager()
login_manager.init_app(app)

# import each controller
from app.controllers.user_controller import Authentication, AuthenticationException, UserController, UserControllerException
from app.controllers.playlist_controller import PlaylistController, PlaylistException
from app.controllers.song_controller import SongController, SongException
from app.controllers.country_controller import CountryController, CountryException
from app.controllers.artist_controller import ArtistController, ArtistException
from app.controllers.album_controller import AlbumController, AlbumException
# from app.controllers.genre_controller import GenreController, GenreException


# instantiate each controller
authentication = Authentication()
user_controller = UserController()
playlist_controller = PlaylistController()
# song_controller = SongController()
country_controller = CountryController()
artist_controller = ArtistController()
album_controller = AlbumController()
# genre_controller = GenreController()


# create engine
engine = create_engine(app.config["DATABASEURI"])

def admin_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    current = current_user
    if current and current.username == 'admin':
      return f(*args, **kwargs)
    abort(401)
  return decorated_function


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
    print "connected!!!"
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


# error handler to send appropriate response
@app.errorhandler(AuthenticationException)
@app.errorhandler(UserControllerException)
@app.errorhandler(PlaylistException)
@app.errorhandler(SongException)
@app.errorhandler(CountryException)
@app.errorhandler(ArtistException)
@app.errorhandler(AlbumException)
# @app.errorhandler(GenreException)
def handle_invalid_usage(error):
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  return response


def date_handler(obj):
  return obj.isoformat() if hasattr(obj, 'isoformat') else obj


# root
@app.route('/')
def index():
  return render_template("index.html")

# login route
@app.route('/api/login', methods=['POST'])
def login():
  username = request.json.get('username')
  password = request.json.get('password')

  user = authentication.authenticate(username, password)
  if user:
    dict_result = {'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name, 'created_at': user.created_at.date()}}
    return json.dumps(dict_result, default=date_handler)

  abort(500)

# signup route
@app.route('/api/signup', methods=['POST'])
def signup():
  username = request.json.get('username')
  password = request.json.get('password')
  first_name = request.json.get('first_name')
  last_name = request.json.get('last_name')

  print username, password, first_name, last_name

  user = authentication.register(username, password, first_name, last_name)
  if user:
    dict_result = {'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name, 'created_at': user.created_at.date()}}
    return json.dumps(dict_result, default=date_handler)
  abort(400)

# logout route
@app.route('/api/logout', methods=['GET', 'POST'])
@login_required
def logout():
  authentication.logout()
  return '', 200

# update account route
@app.route('/api/account', methods=['PUT'])
@login_required
def update_account():
  user_id = current_user.id
  new_user = request.json.get('user')
  user = authentication.update_account(user_id, new_user)
  dict_result = {'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name, 'created_at': user.created_at.date()}}
  return json.dumps(dict_result, default=date_handler)

# update password route
@app.route('/api/account/password', methods=['PUT'])
@login_required
def update_password():
  user_id = current_user.id
  old_pw = request.json.get('password')
  new_pw = request.json.get('new_password')
  user = authentication.update_password(user_id, old_pw, new_pw)
  dict_result = {'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name, 'created_at': user.created_at.date()}}
  return json.dumps(dict_result, default=date_handler)

# get list of users route
@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
  q = request.args.get('q')
  if q:
    users = user_controller.get_users_by_keyword('%' + q.lower() + '%')
  else:
    users = user_controller.get_users()
  return jsonify({'users': users})

@app.route('/api/users/<user_id>', methods=['GET'])
@login_required
def get_user(user_id):
  user_id = int(user_id)
  user = user_controller.get_user(user_id)
  is_current_user = True if int(user_id) == current_user.id else False
  user['is_following'] = user_controller.is_following(current_user.id, user_id)
  user['playlists'] = playlist_controller.get_playlists_for_user(user_id, is_current_user)
  return jsonify({'user': user})

@app.route('/api/users/<user_id>/follow', methods=['POST'])
@login_required
def follow_user(user_id):
  current_user_id = current_user.id
  is_following = user_controller.follow_user(current_user_id, user_id)
  return jsonify({'is_following': is_following})

@app.route('/api/users/<user_id>/unfollow', methods=['POST'])
@login_required
def unfollow_user(user_id):
  current_user_id = current_user.id
  is_following = user_controller.unfollow_user(current_user_id, user_id)
  return jsonify({'is_following': is_following})

@app.route('/api/users/<user_id>/followers', methods=['GET'])
@login_required
def get_followers(user_id):
  followers = user_controller.get_followers(user_id)
  return jsonify({'followers': followers})

@app.route('/api/users/<user_id>/following', methods=['GET'])
@login_required
def get_following(user_id):
  following = user_controller.get_following_users(user_id)
  return jsonify({'following': following})

@app.route('/api/subscription', methods=['GET'])
@login_required
def get_subscription():
  current_user_id = current_user.id
  subscription = user_controller.get_subscription(current_user_id)
  dict_result = {'subscription': subscription}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/subscription', methods=['PUT'])
@login_required
def update_subscription():
  current_user_id = current_user.id
  subscribe_option = request.json.get('subscribe_option')
  subscription = user_controller.update_subscription(current_user_id, subscribe_option)
  dict_result = {'subscription': subscription}
  return json.dumps(dict_result, default=date_handler)


# get list of playlist route
@app.route('/api/playlists', methods=['GET'])
@login_required
def get_playlists():
  q = request.args.get('q')
  if q:
    playlists = playlist_controller.get_public_playlists_for_keyword('%' + q.lower() + '%')
  else:
    playlists = playlist_controller.get_public_playlists()
  return jsonify({'playlists': playlists})

@app.route('/api/playlists/<playlist_id>', methods=['GET'])
@login_required
def get_playlist(playlist_id):
  user_id = current_user.id

  # check if given playlist exists
  playlist = playlist_controller.get_playlist(playlist_id)
  if not playlist:
    abort(404)

  if not playlist['is_public'] and playlist['user_id'] != user_id:
    abort(401)

  # print playlist
  songs = song_controller.get_songs_for_playlist(playlist_id)
  # print songs
  # print len(songs)
  playlist['songs'] = songs

  return jsonify({'playlist': playlist})

@app.route('/api/playlists', methods=['POST'])
@login_required
def create_playlist():
  name = request.json.get('name')
  is_public = request.json.get('is_public')
  user_id = current_user.id
  playlist = playlist_controller.create_playlist(user_id, name, is_public)
  return jsonify({'playlist': playlist})

@app.route('/api/playlists/<playlist_id>', methods=['PUT'])
@login_required
def update_playlist(playlist_id):
  user_id = current_user.id
  name = request.json.get('name')
  is_public = request.json.get('is_public')
  playlist = playlist_controller.update_playlist(user_id, playlist_id, name, is_public)
  return jsonify({'playlist': playlist})

@app.route('/api/playlists/<playlist_id>', methods=['DELETE'])
@login_required
def delete_playlist(playlist_id):
  user_id = current_user.id

  # check if given playlist belongs to current user
  if not playlist_controller.verify_playlist_owner(user_id, playlist_id):
    print 'not user!'
    abort(400)

  # delete playlist
  playlist_controller.delete_playlist(user_id, playlist_id)
  return '', 200

@app.route('/api/playlists/<playlist_id>/songs', methods=['POST'])
@login_required
def add_songs_to_playlist(playlist_id):
  user_id = current_user.id
  # print request.json.get('songs')
  if request.json.get('songs'):
    song_ids = [a['id'] for a in request.json.get('songs')]
  else:
    song_ids = []
  playlist = playlist_controller.add_songs_to_playlist(user_id, playlist_id, song_ids)
  playlist['songs'] = song_controller.get_songs_for_playlist(playlist_id)
  return jsonify({'playlist': playlist})

@app.route('/api/playlists/<playlist_id>/songs/<song_id>', methods=['DELETE'])
@login_required
def delete_song_from_playlist(playlist_id, song_id):
  user_id = current_user.id
  playlist_controller.delete_song_from_playlist(user_id, playlist_id, song_id)
  return '', 200

# @app.route('/api/genres', methods=['GET'])
# @login_required
# def get_genres():
#   q = request.args.get('q')
#   if q:
#     genres = genre_controller.get_genres_for_keyword('%' + q.lower() + '%')
#   else:
#     genres = genre_controller.get_genres()
#   return jsonify({'genres': genres})

# @app.route('/api/genres/<genre_id>', methods=['GET'])
# @login_required
# def get_genre(genre_id):
#   genre = genre_controller.get_genre(genre_id)
#   if not genre:
#     abort(404)
#   genre['albums'] = album_controller.get_albums_for_genre(genre_id)
#   genre['songs'] = song_controller.get_songs_for_genre(genre_id)

#   dict_result = {'genre': genre}
#   return json.dumps(dict_result, default=date_handler)

# @app.route('/api/genres', methods=['POST'])
# @login_required
# def create_genre():
#   name = request.json.get('name')
#   genre = genre_controller.create_genre(name)
#   return jsonify({'genre': genre})

# @app.route('/api/genres/<genre_id>', methods=['PUT'])
# @login_required
# def update_genre(genre_id):
#   name = request.json.get('name')
#   genre = genre_controller.update_genre(genre_id, name)
#   return jsonify({'genre': genre})

# @app.route('/api/genres/<genre_id>', methods=['DELETE'])
# @login_required
# def delete_genre(genre_id):
#   genre_controller.delete_genre(genre_id)
#   return '', 200


@app.route('/api/countries', methods=['GET'])
@login_required
def get_countries():
  q = request.args.get('q')
  if q:
    countries = country_controller.get_countries_for_keyword('%' + q.lower() + '%')
  else:
    countries = country_controller.get_countries()
  return jsonify({'countries': countries})

@app.route('/api/countries/<country_id>', methods=['GET'])
@login_required
def get_country(country_id):
  country = country_controller.get_country(country_id)
  if not country:
    abort(404)
  country['artists'] = artist_controller.get_artists_for_country(country_id)
  return jsonify({'country': country})

@app.route('/api/countries', methods=['POST'])
@login_required
def create_country():
  name = request.json.get('name')
  country = country_controller.create_country(name)
  return jsonify({'country': country})

@app.route('/api/countries/<country_id>', methods=['PUT'])
@login_required
def update_country(country_id):
  name = request.json.get('name')
  country = country_controller.update_country(country_id, name)
  return jsonify({'country': country})

@app.route('/api/countries/<country_id>', methods=['DELETE'])
@login_required
def delete_country(country_id):
  # delete country
  country_controller.delete_country(country_id)
  return '', 200


@app.route('/api/artists', methods=['GET'])
@login_required
def get_artists():
  q = request.args.get('q')
  if q:
    artists = artist_controller.get_artists_for_keyword('%' + q.lower() + '%')
  else:
    artists = artist_controller.get_artists()
  return jsonify({'artists': artists})

@app.route('/api/artists/<artist_id>', methods=['GET'])
@login_required
def get_artist(artist_id):
  artist = artist_controller.get_artist(artist_id)
  if not artist:
    abort(404)
  artist['albums'] = album_controller.get_albums_for_artist(artist_id)
  dict_result = {'artist': artist}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/artists', methods=['POST'])
@login_required
def create_artist():
  name = request.json.get('name')
  country_id = request.json.get('country_id')
  artist = artist_controller.create_artist(name, country_id)
  return jsonify({'artist': artist})

@app.route('/api/artists/<artist_id>', methods=['PUT'])
@login_required
def update_artist(artist_id):
  name = request.json.get('name')
  country_id = request.json.get('country_id')
  artist = artist_controller.update_artist(artist_id, name, country_id)
  return jsonify({'artist': artist})

@app.route('/api/artists/<artist_id>', methods=['DELETE'])
@login_required
def delete_artist(artist_id):
  artist_controller.delete_artist(artist_id)
  return '', 200


@app.route('/api/albums', methods=['GET'])
@login_required
def get_albums():
  q = request.args.get('q')
  if q:
    albums = album_controller.get_albums_for_keyword('%' + q.lower() + '%')
  else:
    albums = album_controller.get_albums()
  dict_result = {'albums': albums}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/albums/<album_id>', methods=['GET'])
@login_required
def get_album(album_id):
  album = album_controller.get_album(album_id)
  if not album:
    album(404)
  album['songs'] = song_controller.get_songs_for_album(album_id)
  album['artists'] = artist_controller.get_artists_for_album(album_id)
  # album['genres'] = genre_controller.get_genres_for_album(album_id)
  dict_result = {'album': album}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/albums', methods=['POST'])
@login_required
def create_album():
  title = request.json.get('title')
  if request.json.get('artist_ids'):
    artist_ids = [a['id'] for a in request.json.get('artist_ids')]
  else:
    artist_ids = []
  if request.json.get('genre_ids'):
    genre_ids = [a['id'] for a in request.json.get('genre_ids')]
  else:
    genre_ids = []
  release_date = request.json.get('release_date')
  album = album_controller.create_album(title, release_date, artist_ids, genre_ids)
  dict_result = {'album': album}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/albums/<album_id>', methods=['PUT'])
@login_required
def update_album(album_id):
  title = request.json.get('title')
  if request.json.get('artist_ids'):
    artist_ids = [a['id'] for a in request.json.get('artist_ids')]
  else:
    artist_ids = []
  if request.json.get('genre_ids'):
    genre_ids = [a['id'] for a in request.json.get('genre_ids')]
  else:
    genre_ids = []
  release_date = request.json.get('release_date')
  album = album_controller.update_album(album_id, title, release_date, artist_ids, genre_ids)
  dict_result = {'album': album}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/albums/<album_id>', methods=['DELETE'])
@login_required
def delete_album(album_id):
  album_controller.delete_album(album_id)
  return '', 200


@app.route('/api/songs', methods=['GET'])
@login_required
def get_songs():
  q = request.args.get('q')
  for_search = request.json.get('for_search') if request.json else None
  if for_search:
    songs =song_controller.get_songs_for_select()
  elif q:
    songs = song_controller.get_songs_for_keyword('%' + q.lower() + '%')
  else:
    songs = song_controller.get_songs()
  dict_result = {'songs': songs}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/songs/<song_id>', methods=['GET'])
@login_required
def get_song(song_id):
  song = song_controller.get_song(song_id)
  if not song:
    song(404)
  dict_result = {'song': song}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/songs', methods=['POST'])
@login_required
def create_song():
  song = request.json.get('song')
  print song
  title = song.get('title')
  duration = song.get('duration')
  url = song.get('url')
  source = song.get('source')
  source_id = song.get('source_id')
  thumbnail = song.get('thumbnail')
  album_id = song.get('album')['id'] if song.get('album') else None
  if song.get('genres'):
    genre_ids = [a['id'] for a in song.get('genres')]
  else:
    genre_ids = []

  song = song_controller.create_song(title, duration, url, source, source_id, thumbnail, album_id, genre_ids)
  dict_result = {'song': song}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/songs/<song_id>', methods=['PUT'])
@login_required
def update_song(song_id):
  song = request.json.get('song')
  title = song.get('title')
  duration = song.get('duration')
  url = song.get('url')
  source = song.get('source')
  source_id = song.get('source_id')
  thumbnail = song.get('thumbnail')
  album_id = song.get('album')['id'] if song.get('album') else None
  if song.get('genres'):
    genre_ids = [a['id'] for a in song.get('genres')]
  else:
    genre_ids = []

  song = song_controller.update_song(song_id, title, duration, url, source, source_id, thumbnail, album_id, genre_ids)
  dict_result = {'song': song}
  return json.dumps(dict_result, default=date_handler)

@app.route('/api/songs/<song_id>', methods=['DELETE'])
@login_required
def delete_song(song_id):
  song_controller.delete_song(song_id)
  return '', 200

@app.route('/api/remaining_playcount', methods=['POST'])
@login_required
def decrement_count():
  user_id = current_user.id
  new_count = user_controller.decrement_count(user_id)
  return jsonify({'remaining_playcount': new_count})