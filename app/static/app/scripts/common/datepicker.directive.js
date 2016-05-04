'use strict';

angular.module('mango').directive("mydatepicker", function(){
  return {
    restrict: "E",
    scope:{
      model: "=",
      dateOptions: "=",
      opened: "=",
    },
    link: function($scope, element, attrs) {
      $scope.open = function(event){
        event.preventDefault();
        event.stopPropagation();
        $scope.opened = true;
      };

      $scope.clear = function () {
        $scope.model = null;
      };

      $scope.maxDate = new Date();
    },
    templateUrl: 'app/views/common/date_picker.html'
  }
});