'use strict';

angular.module('mango').controller('UserController', ['$scope', '$stateParams', '$location', '$timeout', '$rootScope', 'Auth', 'Users',
	function($scope, $stateParams, $location, $timeout, $rootScope, Auth, Users) {
		$scope.getCurrentUser = Auth.getCurrentUser;

		$scope.findOne = function() {
			Users.getUser($stateParams.userId)
			.then(function(user) {
				$scope.user = user;
			}, function(err) {
			});
		};

		$scope.follow = function() {
			Users.follow($stateParams.userId)
			.then(function(res) {
				$scope.user.is_following = true;
				$scope.user.follower_count += 1;
			}, function(err) {
			});
		};

		$scope.unfollow = function() {
			Users.unfollow($stateParams.userId)
			.then(function(res) {
				$scope.user.is_following = false;
				$scope.user.follower_count -= 1;
			}, function(err) {
			});
		};

		$scope.getFollowers = function() {
			Users.getFollowers($stateParams.userId)
			.then(function(res) {
				$scope.followers = res;
			}, function(err) {
			});
		}

		$scope.getFollowing = function() {
			Users.getFollowing($stateParams.userId)
			.then(function(res) {
				$scope.following = res;
			}, function(err) {
			});
		}
	}
]);
