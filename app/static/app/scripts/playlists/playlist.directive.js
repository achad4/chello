'use strict';

angular.module('mango').controller('PlaylistItemController', ['$scope', '$state',
  function($scope, $state) {
    $scope.href = $state.href(
      'viewPlaylist',
      {
        playlistId : $scope.playlist.id
      }
    );
  }
]);

angular.module('mango').directive('playlistItem', function() {
  return {
    restrict : 'EA',
    replace : true,
    templateUrl : 'app/views/playlists/playlist_item.html',
    controller : 'PlaylistItemController',
    scope : {
      playlist : '='
    }
  };
});
