'use strict';

angular.module('mango').controller('SongsController', ['$scope', 'Songs',
	function($scope, Songs) {
		Songs.getSongs()
      .then(function (songs) {
      	$scope.songs = songs;
      });

    $scope.query = '';

    $scope.search = function (e, q) {
      e.preventDefault();
      e.stopPropagation();
      Songs.search(q)
      .then(function (songs) {
      	$scope.query = q;
      	$scope.songs = songs;
      });
    };
	}
]);
