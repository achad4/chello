'use strict';

angular.module('mango').controller('SongItemController', ['$scope', '$state',
  function($scope, $state) {
    $scope.href = $state.href(
      'viewSong',
      {
        songId : $scope.song.id
      }
    );
  }
]);

angular.module('mango').directive('songItem', function() {
  return {
    restrict : 'EA',
    replace : true,
    templateUrl : 'app/views/songs/song_item.html',
    controller : 'SongItemController',
    scope : {
      song : '='
    }
  };
});
