'use strict';

angular.module('mango')
.factory('Auth', ['$http', '$cookies', '$cookieStore', '$q', '$timeout', 'PlayerService', '$rootScope',
	function($http, $cookies, $cookieStore, $q, $timeout, PlayerService, $rootScope) {

	  var currentUser = {};

	  if ($cookieStore.get('currentUser')) {
	    currentUser = $cookieStore.get('currentUser');
	  }

	  return {
	    currentUser : currentUser,
	    login : function (user, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('api/login', {
	        username : user.username,
	        password : user.password
	      })
	      .success(function (res) {
	        var user = res.user;
	        $cookieStore.put('currentUser', user);
	        currentUser = user;

	        $timeout(function () {
	          deferred.resolve(user);
	        }, 300);

	        return cb(user);
	      })
	      .error(function (err) {
	        this.clear();
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },

	    signup : function(user, callback) {
        var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('api/signup', {
	        username : user.username,
	        password : user.password,
	        first_name : user.first_name,
	        last_name : user.last_name
	      })
	      .success(function (res) {
	        var user = res.user;

	        $cookieStore.put('currentUser', user);
	        currentUser = user;

	        $timeout(function () {
	          deferred.resolve(user);
	        }, 300);

	        return cb(user);
	      })
	      .error(function (err) {
	        this.clear();
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
      },

	    logout : function (callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('/api/logout')
	        .success(function (data) {
	        	PlayerService.pause();
	        	$rootScope.currentSong = undefined;
	          this.clear();

	          $timeout(function () {
	            deferred.resolve(data);
	          }, 300);

	          return cb(data);
	        }.bind(this))
	        .error(function (err) {
	          deferred.reject(err);

	          return cb(err);
	        });

	      return deferred.promise;
	    },

	    updateAccount : function(user, callback) {
	    	var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.put('api/account', {
	      	user: user
	      })
	      .success(function (res) {
	      	var user = res.user;

	      	$cookieStore.put('currentUser', user);
	        currentUser = user;

	        $timeout(function () {
	          deferred.resolve(user);
	        }, 300);

	        return cb(user);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },

	    updatePassword : function(credentials, callback) {
	    	var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.put('api/account/password', {
	      	password: credentials.password,
	      	new_password: credentials.new_password
	      })
	      .success(function (res) {
	      	var user = res.user;

	        deferred.resolve(user);

	        return cb(user);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },

	    clear : function () {
	      currentUser = {};
	      $cookieStore.remove('currentUser');
	    },

	    getCurrentUser : function () {
	      return currentUser;
	    },

	    isLoggedIn : function () {
	      return !!currentUser.username;
	    },

	    isLoggedInAsync : function (cb) {
	      if (!!currentUser.$promise) {
	        currentUser.$promise.then(function () {
	          cb(true);
	        })['catch'](function () {
	          cb(false);
	        });
	      } else if (!!currentUser.username) {
	        cb(true);
	      } else {
	        cb(false);
	      }
	    }
	  };
	}
]);