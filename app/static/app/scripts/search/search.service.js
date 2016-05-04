'use strict';

$.getScript('//apis.google.com/js/client.js?onload=loadClient');
var loadClient = function() {
  // console.log('in load yt');
  gapi.client.load('youtube', 'v3')
      .then(function() {
        // console.log('loaded');
      }, function(err) {
        // console.log('in err');
        // console.log(err);
      });
};

// $.getScript('//connect.soundcloud.com/sdk.js');

window.onload = function() {
  console.log('in load sc');
  SC.initialize({
    client_id: '09f27b99ed3eae1eb7b09b77369cbab9'
  });
}

var app = angular.module('mango');

app.factory('SearchService', ['$http', '$q', '$filter', function($http, $q, $filter) {

  var gapiKey = 'AIzaSyDCi4TjCMHkjGeqwXTR0tO1LdNRyWEgJMo';

  var convertYoutubeDuration_ = function(duration) {
    var match = duration.match(/PT(\d+H)?(\d+M)?(\d+S)?/);

    var hours = (parseInt(match[1]) || 0);
    var minutes = (parseInt(match[2]) || 0);
    var seconds = (parseInt(match[3]) || 0);

    return hours * 3600 + minutes * 60 + seconds;
  };

  var processYoutubeSongs = function(response) {
    var songs = [];
    for (var i = 0; i < response.items.length; i++){
      var item = response.items[i];
      var song = {};
      song.title = item.snippet.title;
      song.source_id = item.id;
      song.url = 'http://www.youtube.com/v/'+song.source_id;
      song.thumbnail = item.snippet.thumbnails.default.url;
      song.source = 'youtube';
      song.duration = convertYoutubeDuration_(item.contentDetails.duration);
      songs.push(song);
    }
    return songs;
  };

  var processSoundcloudSongs = function(response) {
    var songs = [];
    response = $filter('orderBy')(response, '-playback_count');
    for (var i = 0; i < response.length; i++){
      var song = {};
      song.title = response[i].title;
      song.source_id = response[i].id.toString();
      song.url = response[i].permalink_url;
      song.thumbnail = response[i].artwork_url;
      song.source = 'soundcloud';
      song.duration = Math.round(response[i].duration/1000);
      songs.push(song);
    }
    return songs;
  };

  return {
    loadSearch : function() {
      loadSearch();
    },

    searchYoutube : function(query) {
      var defYoutube = $q.defer();
      var params = {
        q: query,
        part: 'id',
        type: 'video',
        videoSyndicated: 'true',
        videoEmbeddable: 'true',
        order: 'viewCount',
        maxResults: 20,
        key: gapiKey
      };

      function success(response) {
        var videoIDs = [];
        for (var i = 0; i < response.result.items.length; i++) {
          videoIDs.push(response.result.items[i].id.videoId);
        }
        var params = {
          id: videoIDs.join(),
          part: 'contentDetails, snippet',
          key: gapiKey
        };

        gapi.client.youtube.videos.list(params).execute(function(res) { // jshint ignore:line
          defYoutube.resolve(processYoutubeSongs(res));
        });
      }

      function failure(fault) {
        defYoutube.reject(fault);
      }

      gapi.client.youtube.search.list(params).then(success, failure); // jshint ignore:line
      return defYoutube.promise;
    },

    searchSoundcloud : function(query) {
      var defSC = $q.defer();

      var params = {
        q: query,
        limit: 20,
        streamable: true,
        filter: 'all'
      };

      SC.get('/tracks', params).then(function(response) { // jshint ignore:line
        console.log('in res');
        defSC.resolve(processSoundcloudSongs(response));
      }); 

      return defSC.promise;
    }

  };

}]);
