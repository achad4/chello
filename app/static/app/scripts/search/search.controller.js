'use strict';

angular.module('mango').controller('SearchController', ['$scope', '$stateParams', 'SearchService', 'Playlists', 'Songs',
  function($scope, $stateParams, SearchService, Playlists, Songs) {
    $scope.busy = false;

    $scope.youtube = null;
    $scope.soundcloud = null;

    $scope.searchSong = function() {
      console.log('search q:' + $scope.q);
      $scope.youtube = null;
      $scope.soundcloud = null;
      // if (SearchService.isGAPILoaded()) {
        // SearchService.searchByTrackName($scope.q)
        // .then(function(res) {

        //   for (var i=0; i<res.length; i++) {
        //     console.log(res[i]);
        //     if (res[i][0].source === 'youtube') {
        //       $scope.youtube = res[i];
        //     }
        //     else if (res[i][0].source === 'soundcloud') {
        //       $scope.soundcloud = res[i];
        //     }
        //   }
        // })
        // .finally(function() {
        //   $scope.busy = false;
        // });
      // }
      // else {
      //   setTimeout(function() { $scope.searchSong(); }, 50);
      // }
      SearchService.searchYoutube($scope.q)
      .then(function(res) {
        console.log(res);
        $scope.youtube = res;
      });
      SearchService.searchSoundcloud($scope.q)
      .then(function(res) {
        console.log(res);
        $scope.soundcloud = res;
      });
    };

    $scope.addSong = function(song) {
      $scope.error = null;
      var playlist = $scope.playlist;
      $scope.playlist = Playlists.getPlaylist($stateParams.playlistId);
      console.log($scope.playlist);
      console.log('song clicked');
      console.log(song.title);
      Songs.addSong($scope.playlist.id, song)
      .then(
        function(song) {
          $scope.playlist.songs.append(song);
        }, function(err) {
          $scope.error = err;
        });
      // $scope.playlist.$addSong({playlistId: $stateParams.playlistId, song: $.param(song)}).then(function(res) {
      //   console.log(res);
      // });
    };

}]);
