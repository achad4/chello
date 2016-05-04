'use strict';

angular.module('mango')
.factory('Songs', ['$http', '$q', '$timeout', 
	function($http, $q, $timeout) {

	  return {
	    getSongsForPlaylist : function (playlist_id, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/playlists' + playlist_id)
	      .success(function (res) {
	        var songs = res.songs;

	        $timeout(function () {
	          deferred.resolve(songs);
	        }, 300);

	        return cb(songs);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    addSongsToPlaylist : function (playlist_id, songs, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('api/playlists/' + playlist_id + '/songs', {
	        songs: songs
	      })
	      .success(function (res) {
	      	console.log(res);
	      	// console.log(songs);
	        var playlist = res.playlist;

	        $timeout(function () {
	          deferred.resolve(playlist);
	        }, 300);

	        return cb(playlist);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    deleteSongFromPlaylist : function (playlist_id, song_id, callback) {
	    	// console.log(song_id);
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.delete('api/playlists/' + playlist_id + '/songs/' + song_id)
	      .success(function (res) {
	        $timeout(function () {
	          deferred.resolve(res);
	        }, 300);

	        return cb(res);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    getSongs : function (callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/songs')
	      .success(function (res) {
	      	console.log(res);
	        var songs = res.songs;

	        $timeout(function () {
	          deferred.resolve(songs);
	        }, 300);

	        return cb(songs);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    getSongsForSelect : function (callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/songs', {
	      	for_search: true
	      })
	      .success(function (res) {
	      	console.log(res);
	        var songs = res.songs;

	        $timeout(function () {
	          deferred.resolve(songs);
	        }, 300);

	        return cb(songs);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    createSong : function (song, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('api/songs', {
	      	song: song
	      })
	      .success(function (res) {
	        var song = res.song;

	        $timeout(function () {
	          deferred.resolve(song);
	        }, 300);

	        return cb(song);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    editSong : function (songId, song, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.put('api/songs/' + songId, {
	      	song: song
	      })
	      .success(function (res) {
	        var song = res.song;

	        $timeout(function () {
	          deferred.resolve(song);
	        }, 300);

	        return cb(song);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    deleteSong : function (songId, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.delete('api/songs/' + songId)
	      .success(function (res) {
	        $timeout(function () {
	          deferred.resolve(res);
	        }, 300);

	        return cb(res);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    search : function (q, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/songs?q='+q)
	      .success(function (res) {
	        var songs = res.songs;

	        $timeout(function () {
	          deferred.resolve(songs);
	        }, 300);

	        return cb(songs);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    getSong : function (songId, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/songs/' + songId)
	      .success(function (res) {
	        var song = res.song;

	        $timeout(function () {
	          deferred.resolve(song);
	        }, 300);

	        return cb(song);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    }
	  };

	}
]);
