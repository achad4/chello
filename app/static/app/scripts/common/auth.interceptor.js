'use strict';

angular.module('mango')
.factory('AuthInterceptor', ['$q', '$cookieStore', '$location', '$injector', 
  function($q, $cookieStore, $location, $injector) {
    var Auth;

    return {
      'responseError' : function (res) {
        if (!Auth) {
          Auth = $injector.get('Auth');
        }

        if (res.status === 401) {
          Auth.clear();
          $location.path('/login');
        }

        else if (res.status === 404) {
          $location.path('/404');
        }

        return $q.reject(res);
      }
    };

  }
]);
