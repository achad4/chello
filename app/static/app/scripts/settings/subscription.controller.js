'use strict';

angular.module('mango')
.controller('SubscriptionController', ['$scope', 'Auth', 'Users',
	function ($scope, Auth, Users) {
    $scope.error = null;

    $scope.getCurrentUser = function() {
      $scope.user = Auth.getCurrentUser();
    }

    $scope.getSubscription = function() {
      Users.getSubscription()
      .then(function(subscription) {
        $scope.subscription = subscription;
        $scope.error = null;
      }, function(err) {
        $scope.error = err.message;
      });
    };

    $scope.unsubscribe = function() {
      Users.updateSubscription(false)
      .then(function(subscription) {
        $scope.subscription = subscription;
        $scope.error = null;
      }, function(err) {
        $scope.error = err.message;
      });
    };

    $scope.subscribe = function() {
      Users.updateSubscription(true)
      .then(function(subscription) {
        $scope.subscription = subscription;
        $scope.error = null;
      }, function(err) {
        $scope.error = err.message;
      });
    };
	}
]);
