'use strict';

var app = angular.module('mango');

app.factory('PlayerService', ['$http', '$q', '$window', '$rootScope', '$timeout',
  function($http, $q, $window, $rootScope, $timeout) {
    var playerReady = false;

    var youtubePaused = false;
    var soundcloudPaused = false;
    var youtubePlaying = false;
    var soundcloudPlaying = false;


    // load youtube iframe player
    var youtubePlayer;
    var tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';

    var loadPlayers = function() {
      var firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

      $window.onYouTubeIframeAPIReady = function() {
        youtubePlayer = new YT.Player('player', {
          height: '0',
          width: '0',
          events: {
            'onReady': youtubePlayerReady,
            'onStateChange': youtubeOnStateChange,
            'onError': youtubeOnError
          }
        });
      };
      playerReady = true;
    };
    
    var playlist;
    var index;
    var soundObj;
    var self = this;

    var playSoundcloud = function(song) {
      stopSoundcloud();
      SC.stream("/tracks/" + song.source_id).then(function(sound){
          soundObj = sound;
          youtubePlaying = false;
          soundcloudPlaying = true;
          soundObj.play();
          soundObj.on('finish', function() {
            // console.log('playing next');
            playNext();
          });
      });
    };

    var stopSoundcloud = function() {
      if (soundObj !== undefined) {
        soundObj.pause();
        soundObj.seek(0);
      }
    };

    var pauseSoundcloud = function() {
      if (soundObj !== undefined) {
        soundObj.pause();
        soundcloudPlaying = false;
        soundcloudPaused = true;
        youtubePaused = false;
      }
    };

    var resumeSoundcloud = function() {
      if (soundObj !== undefined) {
        soundObj.play();
        soundcloudPaused = false;
        soundcloudPlaying = true;
        youtubePlaying = false;
      }
    };

    var youtubePlayerReady = function(event) {
      // console.log('player is ready!');
    };

    var youtubeOnStateChange = function(event) {
      if (event.data === YT.PlayerState.ENDED) {
        playNext();
      }
    };

    var youtubeOnError = function(event) {
      playNext();
    };

    var playYoutube = function(song) {
      soundcloudPlaying = false;
      youtubePlaying = true;
      youtubePlayer.loadVideoById(song.source_id, 0, 'large');
      youtubePlayer.playVideo();
    };

    var stopYoutube = function() {
      youtubePlayer.stopVideo();
    };

    var pauseYoutube = function() {
      youtubePlayer.pauseVideo();
      youtubePaused = true;
      youtubePlaying = false;
      soundcloudPaused = false;
    };

    var resumeYoutube = function() {
      soundcloudPlaying = false;
      youtubePlaying = true;
      youtubePaused = false;
      youtubePlayer.playVideo();
    };

    var playNext = function() {
      if (playlist !== undefined) {
          soundcloudPaused = false;
          youtubePaused = false;
          playSong(index);
      }
    };

    var playPrev = function() {
      if (playlist !== undefined) {
          soundcloudPaused = false;
          youtubePaused = false;
          playSong(index-2);
      }
    };

    var resume = function() {
      $timeout(function () {
          $rootScope.$apply(function () {
              $rootScope.playing = true;
          });
      }, 300);
      if (soundcloudPaused == true) {
        soundcloudPaused = false;
        resumeSoundcloud();
      }
      else if (youtubePaused == true) {
        youtubePaused = false;
        resumeYoutube();
      }
    }

    var playSong = function(songIndex) {
      var song = playlist.songs[songIndex];
      if (song !== undefined) {
        $http.post('api/remaining_playcount')
        .success(function (res) {
          $timeout(function () {
              $rootScope.$apply(function () {
                  $rootScope.currentSong = song;
                  console.log(song);
                  $rootScope.playing = true;
              });
          }, 300);
          if (song.source === 'soundcloud') {
            playSoundcloud(song);
            stopYoutube();
          }
          else if (song.source === 'youtube') {
            playYoutube(song);
            stopSoundcloud();
          }
          index = songIndex + 1;
          $rootScope.remaining_playcount = res.remaining_playcount;
        }).error(function (err) {
          console.log("in error");
          console.log(err);
          $rootScope.remaining_playcount = 0;
        });
      }
      else {
        $timeout(function () {
            $rootScope.$apply(function () {
                $rootScope.currentSong = null;
                $rootScope.playing = false;
                stopYoutube();
                stopSoundcloud();
            });
        }, 300);
      }
    };

    return {

      loadPlayers : function() {
        loadPlayers();
      },

      loadPlaylist : function(newPlaylist) {
        var def = $q.defer();
        playlist = newPlaylist;
        index = 0;

        $timeout(function () {
            $rootScope.$apply(function () {
                $rootScope.currentPlaylist = newPlaylist;
            });
        }, 300);

        def.resolve(index);

        return def.promise;
      },

      play : function() {
        playNext();
      },

      next : function() {
        playNext();
      },

      prev : function() {
        playPrev();
      },

      playSong : function(newPlaylist, songIndex) {
        $timeout(function () {
            $rootScope.$apply(function () {
                $rootScope.currentPlaylist = newPlaylist;
            });
        }, 300);
        playlist = newPlaylist;
        playSong(songIndex);
      },

      pause : function() {
        $timeout(function () {
            $rootScope.$apply(function () {
                $rootScope.playing = false;
            });
        }, 300);
        if (soundcloudPlaying == true) {
          pauseSoundcloud();
        }
        if (youtubePlaying == true) {
          pauseYoutube();
        }
      },

      isPaused : function() {
        return (soundcloudPaused || youtubePaused) && playlist !== null;
      },

      isPlaying : function() {
        return youtubePlaying || soundcloudPlaying;
      },

      resume : function() {
        resume();
      }
    };

}]);
