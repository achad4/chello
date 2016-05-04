'use strict';

angular.module('mango').controller('UsersController', ['$scope', 'Users',
	function($scope, Users) {
		Users.getUsers()
      .then(function (users) {
      	$scope.users = users;
      	// console.log(users);
      });

    $scope.query = '';

    $scope.search = function (e, q) {
      e.preventDefault();
      e.stopPropagation();
      Users.search(q)
      .then(function (users) {
      	$scope.query = q;
      	$scope.users = users;
        console.log(users);
      });
    };
	}
]);
