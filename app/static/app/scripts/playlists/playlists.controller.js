'use strict';

angular.module('mango').controller('PlaylistsController', ['$scope', 'Playlists',
	function($scope, Playlists) {
		Playlists.getPlaylists()
      .then(function (playlists) {
      	$scope.playlists = playlists;
      });

    $scope.query = '';

    $scope.search = function (e, q) {
      e.preventDefault();
      e.stopPropagation();
      Playlists.search(q)
      .then(function (playlists) {
      	$scope.query = q;
      	$scope.playlists = playlists;
      });
    };
	}
]);
