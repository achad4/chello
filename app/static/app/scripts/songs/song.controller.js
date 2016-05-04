'use strict';

angular.module('mango').controller('SongController', ['$scope', '$stateParams', '$location', '$timeout', '$rootScope', '$modal', '$filter', 'Auth', 'Songs','Albums','Genres', 'PlayerService',
	function($scope, $stateParams, $location, $timeout, $rootScope, $modal, $filter, Auth, Songs, Albums, Genres, PlayerService) {
		$scope.getCurrentUser = Auth.getCurrentUser;
		$scope.song = {};

		$scope.findOne = function() {
			Songs.getSong($stateParams.songId)
			.then(function(song) {
				console.log(song);
				$scope.song = song;
				$scope.duration = $filter('secondsToDateTime')($scope.song.duration);
        $scope.duration = $filter('date')($scope.duration, 'm:ss');
			}, function(err) {
			});
		};

		$scope.create = function() {
			Songs.createSong($scope.song)
			.then(function(song) {
				$location.path('songs/' + song.id);
			},
			function(err) {
				$scope.error = err.message;
			});
		};

		$scope.edit = function() {
			Songs.editSong($stateParams.songId, $scope.song)
			.then(function(song) {
				$location.path('songs/' + song.id);
			},
			function(err) {
				$scope.error = err.message;
			});
		};

		$scope.deleteSong = function() {
			Songs.deleteSong($stateParams.songId)
				.then(function() {
					$location.path('songs');
				},
				function(err) {
					$scope.error = err.message;
				});
		};

		$scope.getAlbums = function() {
			Albums.getAlbums()
      .then(function (albums) {
      	$scope.albums = albums;
      });
		}

		$scope.getGenres = function() {
			Genres.getGenres()
      .then(function (genres) {
      	$scope.genres = genres;
      });
		}

		$scope.openModal = function() {
			$modal.open({
        templateUrl: 'app/views/songs/modal_selector.html',
        controller: 'ModalInstanceController',
        size: 'md',
        scope: $scope
      })
      .result
      .then(function (song) {
        $scope.song = song;
        $scope.duration = $filter('secondsToDateTime')(song.duration);
        $scope.duration = $filter('date')($scope.duration, 'm:ss');
      });
		}

		$scope.play = function() {
			$scope.song_array = {'id': 0};
			$scope.song_array.songs = [];
			$scope.song_array.songs.push($scope.song);
			PlayerService.loadPlaylist($scope.song_array)
			.then(function() {
				PlayerService.play();
			});
		};

		$scope.pause = function() {
			PlayerService.pause();
		};
	}
])
.controller('ModalInstanceController', ['$scope', '$stateParams', '$modalInstance', 'SearchService',
  function($scope, $stateParams, $modalInstance, SearchService) {
    $scope.q = $stateParams.q;
    $scope.type = $stateParams.type;
    $scope.youtubeSelected = true;

    $scope.busy = false;

    $scope.youtube = null;
    $scope.soundcloud = null;

    $scope.searchSong = function() {
      $scope.youtube = null;
      $scope.soundcloud = null;
      SearchService.searchYoutube($scope.q)
      .then(function(res) {
        $scope.youtube = res;
      });
      SearchService.searchSoundcloud($scope.q)
      .then(function(res) {
        $scope.soundcloud = res;
      });
    };

    $scope.select = function(selected) {
			if (selected == 'youtube') {
				$scope.youtubeSelected = true;
			}
			else {
				$scope.youtubeSelected = false;
			}
		};

    $scope.setSong = function(song) {
    	$modalInstance.close(song);
    }
}]);
