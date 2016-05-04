'use strict';

angular.module('mango').directive('sideNav', function() {
  return {
    restrict : 'EA',
    controller : 'NavbarController',
    templateUrl : 'app/views/common/side_nav.html'
  };
});
