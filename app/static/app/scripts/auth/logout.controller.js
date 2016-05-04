'use strict';

angular.module('mango')
  .controller('LogoutController', ['$scope', '$location', 'Auth', '$rootScope', '$timeout',
  	function ($scope, $location, Auth, $rootScope, $timeout) {
      Auth.logout()
        .then(function (data) {
        	$timeout(function () {
            $rootScope.$apply(function () {
                $rootScope.playing = false;
                $rootScope.currentPlaylist = null;
                $rootScope.currentSong = null;
            });
        }, 300);
          $location.path('/login');
        });
  }]);
