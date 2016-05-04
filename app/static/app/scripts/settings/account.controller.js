'use strict';

angular.module('mango')
.controller('AccountController', ['$scope', 'Auth', 'Modals',
	function ($scope, Auth, Modals) {
    $scope.error = null;

    $scope.getCurrentUser = function() {
      $scope.user = Auth.getCurrentUser();
    }

    $scope.save = function() {
      Auth.updateAccount($scope.user)
      .then(function(user) {
        $scope.user = user;
        $scope.error = null;
      }, function(err) {
        $scope.error = err.message;
      });
    };

    $scope.changePassword = function() {
      Modals.open($scope,'app/views/settings/update_password.html');
    };

    $scope.savePassword = function(credentials) {
      Auth.updatePassword(credentials)
      .then(function() {
        $scope.password_error = null;
        $scope.closeModal();
      }, function(err) {
        $scope.password_error = err.message;
      });
    }

    $scope.closeModal = function() {
      Modals.close();
    };
	}
]);
