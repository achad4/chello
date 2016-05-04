'use strict';

angular.module('mango')
  .controller('LoginController', ['$scope', '$location', 'Auth', function ($scope, $location, Auth) {
  	$scope.login = function login() {
      Auth.login($scope.credentials)
        .then(function (user) {
        	$location.path('/');
        }, function(err) {
          $scope.error = err.message;
        });
    };
  }]);
