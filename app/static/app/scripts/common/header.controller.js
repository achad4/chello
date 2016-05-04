'use strict';

angular.module('mango').controller('HeaderController', ['$scope', 'Auth', '$location', 'PlayerService',
	function($scope, Auth, $location, PlayerService) {
		// console.log('header controller');
		$scope.getCurrentUser = Auth.getCurrentUser;
		$scope.isLoggedIn = Auth.isLoggedIn;

		$scope.logout = function logout() {
      Auth.logout().then(function () {
      	PlayerService.pause();
        $location.path('/login');
      });
    };

    $scope.isCollapsed = false;

		$scope.toggleCollapsibleMenu = function toggleCollapsibleMenu() {
			$scope.isCollapsed = !$scope.isCollapsed;
		};
	}
]);
