'use strict';

// Declare app level module which depends on filters, and services
angular.module('mango', ['ngResource','ui.router', 'ngCookies', 'ui.bootstrap', 'ui.select'])
  .config(['$urlRouterProvider', '$httpProvider', '$stateProvider', function ($urlRouterProvider, $httpProvider, $stateProvider) {
    $urlRouterProvider.otherwise( '/' );
    $httpProvider.interceptors.push('AuthInterceptor');
    $stateProvider
      .state('home', {
        url: '/',
        authenticate: true,
        controller: 'HomeController',
        templateUrl: 'app/views/common/home.html'
      })
      .state('notFoundPage', {
        url: '/404',
        templateUrl: 'app/views/common/404.html'
      })
      .state('login', {
        url : '/login',
        controller : 'LoginController',
        templateUrl : 'app/views/auth/login.html'
      })
      .state('signup', {
        url : '/signup',
        controller : 'SignupController',
        templateUrl : 'app/views/auth/signup.html'
      })
      .state('logout', {
        url : '/logout',
        authenticate: true,
        controller : 'LogoutController',
        templateUrl : 'app/views/auth/login.html'
      })
      .state('account', {
        url : '/account_settings',
        controller : 'AccountController',
        templateUrl : 'app/views/settings/account.html',
        authenticate: true
      })
      .state('subscription', {
        url: '/subscription',
        authenticate: true,
        controller: 'SubscriptionController',
        templateUrl: 'app/views/settings/subscription.html'
      })
      
      .state('playlists', {
        url: '/playlists',
        authenticate: true,
        controller: 'PlaylistsController',
        templateUrl: 'app/views/playlists/playlists.html'
      })
      .state('createPlaylist', {
        url: '/playlists/new',
        authenticate: true,
        controller : 'PlaylistController',
        templateUrl : 'app/views/playlists/create_playlist.html'
      })
      .state('viewPlaylist', {
        url: '/playlists/:playlistId',
        authenticate: true,
        controller : 'PlaylistController',
        templateUrl: 'app/views/playlists/playlist.html'
      })
      .state('editPlaylist', {
        url: '/playlists/:playlistId/edit',
        authenticate: true,
        controller : 'PlaylistController',
        templateUrl: 'app/views/playlists/edit_playlist.html'
      })

      .state('songs', {
        url: '/songs',
        authenticate: true,
        controller: 'SongsController',
        templateUrl: 'app/views/songs/songs.html'
      })

      .state('users', {
        url: '/users',
        authenticate: true,
        controller: 'UsersController',
        templateUrl: 'app/views/users/users.html'
      })
      .state('viewUser', {
        url: '/users/:userId',
        authenticate: true,
        controller: 'UserController',
        templateUrl: 'app/views/users/user.html'
      })
      .state('viewFollowers', {
        url: '/users/:userId/followers',
        authenticate: true,
        controller: 'UserController',
        templateUrl: 'app/views/users/follower.html'
      })
      .state('viewFollowing', {
        url: '/users/:userId/following',
        authenticate: true,
        controller: 'UserController',
        templateUrl: 'app/views/users/following.html'
      });
  }])
  .run(['$rootScope', '$location', '$window', 'Auth', 'PlayerService', 'SearchService', 
    function($rootScope, $location, $window, Auth, PlayerService, SearchService) {
      PlayerService.loadPlayers();
      $rootScope.$on('$stateChangeStart', function (event, next) {
        $window.scrollTo(0, 0);

        Auth.isLoggedInAsync(function (isLoggedIn) {
          if (isLoggedIn && (next.name === 'home' || next.name === 'signup' || next.name === 'login')) {
            $location.path('/playlists');
          }

          if (next.authenticate && !isLoggedIn) {
            $location.path('/login');
          }
        });
      });
    }
  ])
  ;
