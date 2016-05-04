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
