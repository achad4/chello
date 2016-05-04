'use strict';

angular.module('mango').controller('UserItemController', ['$scope', '$state',
  function($scope, $state) {
    $scope.href = $state.href(
      'viewUser',
      {
        userId : $scope.user.id
      }
    );
  }
]);

angular.module('mango').directive('userItem', function() {
  return {
    restrict : 'EA',
    replace : true,
    templateUrl : 'app/views/users/user_item.html',
    controller : 'UserItemController',
    scope : {
      user : '='
    }
  };
});
