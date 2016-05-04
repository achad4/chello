'use strict';

angular.module('mango')
.controller('NavbarController', ['$scope', 'Auth', '$location',
	function ($scope, Auth, $location) {
  	$scope.logout = function() {
  		Auth.logout()
        .then(function (data) {
          $location.path('/login');
        });
  	}

  	$scope.getUsername = function() {
      $scope.currentUser = Auth.getCurrentUser();
  	}

    $scope.isActive = function(route) {
      if (route === '/users')
        return $location.path().indexOf(route) === 0 && $location.path().indexOf('/users/' + $scope.currentUser.id) < 0;
      return $location.path().indexOf(route) === 0;
    }
	}
]);
