'use strict';

angular.module('mango')
  .controller('SignupController', ['$scope', '$location', 'Auth', function ($scope, $location, Auth) {
  	$scope.signup = function signup() {
  		$scope.error = null;
      Auth.signup($scope.credentials)
        .then(function (data) {
          $location.path('/');
        }, function(err) {
        	$scope.error = err.message;
        });
    };
  }]);
