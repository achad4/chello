'use strict';

angular.module('mango').controller('PlaylistController', ['$scope', '$stateParams', '$location', 'Playlists', 'PlayerService', 'SearchService', 'Songs', '$timeout', '$rootScope', 'Auth', '$modal', '$state',
	function($scope, $stateParams, $location, Playlists, PlayerService, SearchService, Songs, $timeout, $rootScope, Auth, $modal, $state) {
		$scope.isPlaying = PlayerService.isPlaying;
		$scope.isPaused = PlayerService.isPaused;
		$scope.youtubeSelected = true;

		$scope.getCurrentUser = Auth.getCurrentUser;

		$scope.select = function(selected) {
			if (selected == 'youtube') {
				$scope.youtubeSelected = true;
			}
			else {
				$scope.youtubeSelected = false;
			}
		};

		$scope.create = function() {
			// console.log('in create');
			Playlists.createPlaylist($scope.name, $scope.is_public)
			.then(function(playlist) {
				$location.path('playlists/' + playlist.id);
			},
			function(err) {
				// console.log(err.message);
				$scope.error = err.message;
			});
		};

		$scope.edit = function() {
			Playlists.editPlaylist($stateParams.playlistId, $scope.playlist.name, $scope.playlist.is_public)
				.then(function(playlist) {
					$location.path('playlists/' + playlist.id);
				},
				function(err) {
					// console.log(err.message);
					$scope.error = err.message;
				});
		};

		$scope.deletePlaylist = function() {
			Playlists.deletePlaylist($stateParams.playlistId)
				.then(function() {
					PlayerService.pause();
					$location.path('playlists');
				},
				function(err) {
					// console.log(err.message);
					$scope.error = err.message;
				});
		};

		$scope.find = function() {
			$scope.playlists = Playlists.getPlaylists();
		};

		$scope.findOne = function() {
			// console.log($stateParams.playlistId);

			Playlists.getPlaylist($stateParams.playlistId)
			.then(function(playlist) {
				$scope.playlist = playlist;
				console.log(playlist);
			}, function(err) {
				// console.log(err);
			});
		};

		$scope.play = function() {
			if (PlayerService.isPaused() && $rootScope.currentPlaylist.id === $scope.playlist.id) {
				PlayerService.resume();
				// $timeout(function () {
	   //        $scope.$apply(function () {
	   //        	$scope.playing = true;
	   //        });
	   //    }, 300);
				// $scope.playing = true;
			}
			else {
				PlayerService.loadPlaylist($scope.playlist)
				.then(function() {
					PlayerService.play();
					// $timeout(function () {
		   //        $scope.$apply(function () {
		   //        	$scope.playing = true;
		   //        });
		   //    }, 300);
		      // $scope.playing = true;
				});
			}
		};

		$scope.resume = function() {
			PlayerService.resume();
		};

		$scope.playSong = function(index) {
			if ($rootScope.currentSong && $rootScope.currentSong.url === $scope.playlist.songs[index].url && $rootScope.playing) {
				$scope.pause();
			}
			else if ($rootScope.currentSong && $rootScope.currentSong.url === $scope.playlist.songs[index].url && !$rootScope.playing) {
				PlayerService.resume();
				// $timeout(function () {
	   //        $scope.$apply(function () {
	   //        	$scope.playing = true;
	   //        });
	   //    }, 300);
				// $scope.playing = true;
			}
			else {
				PlayerService.playSong($scope.playlist, index);
				// $timeout(function () {
	   //        $scope.$apply(function () {
	   //        	$scope.playing = true;
	   //        });
	   //    }, 300);
				// $scope.playing = true;
			}
		};

		$scope.pause = function(index) {
			// console.log('pressed pause song');
			PlayerService.pause();
			
			// $timeout(function () {
   //        $scope.$apply(function () {
   //        	$scope.playing = false;
   //        });
   //    }, 300);
			// $scope.playing = false;
		};

		$scope.next = function() {
			PlayerService.next();
		};

		$scope.prev = function() {
			PlayerService.prev();
		};

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

    $scope.addSongs = function(songs) {
      $scope.error = null;
      Songs.addSongsToPlaylist($stateParams.playlistId, songs)
      .then(
        function(playlist) {
        	for (var i=0; i<songs.length; i++)
          	$scope.playlist = playlist;
          // $scope.getUrl();
        }, function(err) {
          $scope.error = err;
        });
    };

    $scope.deleteSong = function($event, song_id, index) {
    	$event.stopPropagation();
    	$scope.error = null;
    	Songs.deleteSongFromPlaylist($stateParams.playlistId, song_id)
    	.then(
    		function() {
    			$scope.playlist.songs.splice(index, 1);
    		}, function(err) {
    			$scope.error = err;
    		});
    };

    $scope.viewDetails = function($event, song_id) {
    	$event.stopPropagation();
    	$scope.error = null;
    	$state.go('viewSong', {'songId':song_id});
    };

    $scope.openModal = function() {
			$modal.open({
        templateUrl: 'app/views/playlists/add_modal.html',
        controller: 'PlaylistModalController',
        size: 'md',
        scope: $scope
      })
      .result
      .then(function (songs) {
      	console.log(songs);
      	$scope.addSongs(songs);
      });
		}


    // $scope.currentUrl = null;
    // $scope.$on(
    //     "updateNowPlaying",
    //     function handleUpdateUrl(event, currentSong) {
    //     	console.log('updated now playing!!');
    //     	console.log(currentSong);
    //       $scope.currentSong = currentSong;
    //       console.log($scope.currentSong);
    //     }
    // );

    $scope.currentSong = $scope.currentSong;

    // $scope.getUrl = PlayerService.getUrl;
		
		// $scope.removeSong = function(songId) {
		// 	console.log('removing song');
		// 	console.log(songId);
		// 	$scope.playlist.$removeSong({playlistId: $stateParams.playlistId, songId: songId});
		// };
	}
])
.controller('PlaylistModalController', ['$scope', '$stateParams', '$modalInstance', 'Songs', '$state',
  function($scope, $stateParams, $modalInstance, Songs, $state) {
    $scope.q = $stateParams.q;
    $scope.type = $stateParams.type;

    $scope.busy = false;
    $scope.select = {};
    // $scope.selectedSongs = [];

    $scope.getSongs = function() {
			Songs.getSongsForSelect()
      .then(function (songs) {
      	$scope.songs = songs;
      });
		}

    $scope.addSongs = function() {
    	$modalInstance.close($scope.select.songs);
    }

    $scope.redirectToAdd = function() {
    	$modalInstance.dismiss();
    	$state.go('createSong');
    }
}]);
