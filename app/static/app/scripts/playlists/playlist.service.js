'use strict';

angular.module('mango')
.factory('Playlists', ['$http', '$q', '$timeout', 
	function($http, $q, $timeout) {

	  return {
	    getPlaylists : function (callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/playlists')
	      .success(function (res) {
	        var playlists = res.playlists;

	        $timeout(function () {
	          deferred.resolve(playlists);
	        }, 300);

	        return cb(playlists);
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

	      $http.get('api/playlists?q='+q)
	      .success(function (res) {
	        var playlists = res.playlists;

	        $timeout(function () {
	          deferred.resolve(playlists);
	        }, 300);

	        return cb(playlists);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    getPlaylist : function (playlist_id, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/playlists/' + playlist_id)
	      .success(function (res) {
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
	    createPlaylist : function (name, is_public, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('api/playlists', {
	      	name: name,
	      	is_public: is_public
	      })
	      .success(function (res) {
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
	    editPlaylist : function (playlistId, name, is_public, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.put('api/playlists/' + playlistId, {
	      	name: name,
	      	is_public: is_public
	      })
	      .success(function (res) {
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
	    deletePlaylist : function (playlistId, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.delete('api/playlists/' + playlistId)
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
	    }
	  };

	}
]);
