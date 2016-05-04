'use strict';

angular.module('mango')
.factory('Users', ['$http', '$q', '$timeout', 
	function($http, $q, $timeout) {

	  return {
	    getUsers : function (callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/users')
	      .success(function (res) {
	        var users = res.users;

	        $timeout(function () {
	          deferred.resolve(users);
	        }, 300);

	        return cb(users);
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

	      $http.get('api/users?q='+q)
	      .success(function (res) {
	        var users = res.users;

	        $timeout(function () {
	          deferred.resolve(users);
	        }, 300);

	        return cb(users);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    getUser : function (user_id, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/users/' + user_id)
	      .success(function (res) {
	      	var user = res.user;
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
	    follow : function (user_id, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('api/users/' + user_id + '/follow')
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
	    unfollow : function (user_id, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.post('api/users/' + user_id + '/unfollow')
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
	    getFollowing : function (user_id, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/users/' + user_id + '/following')
	      .success(function (res) {
	      	var following = res.following;
	        $timeout(function () {
	          deferred.resolve(following);
	        }, 300);

	        return cb(following);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    getFollowers : function (user_id, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/users/' + user_id + '/followers')
	      .success(function (res) {
	      	var followers = res.followers;
	        $timeout(function () {
	          deferred.resolve(followers);
	        }, 300);

	        return cb(followers);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    getSubscription : function (callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.get('api/subscription')
	      .success(function (res) {
	      	var subscription = res.subscription;
	        $timeout(function () {
	          deferred.resolve(subscription);
	        }, 300);

	        return cb(subscription);
	      })
	      .error(function (err) {
	        deferred.reject(err);

	        return cb(err);
	      }.bind(this));

	      return deferred.promise;
	    },
	    updateSubscription : function (subscribe_option, callback) {
	      var cb = callback || angular.noop,
	          deferred = $q.defer();

	      $http.put('api/subscription', {
	      	subscribe_option: subscribe_option
	      })
	      .success(function (res) {
	      	var subscription = res.subscription;
	      	console.log(subscription);
	        $timeout(function () {
	          deferred.resolve(subscription);
	        }, 300);

	        return cb(subscription);
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
