'use strict';

angular.module('mango')
.factory('Modals', ['$modal', 
	function($modal) {
		var modalInstance = null;

	  return {
	    open : function (scope, path) {
        modalInstance = $modal.open({
          templateUrl: path,
          scope: scope
        });
	    },
	    close : function() {
	    	modalInstance.dismiss('close');
	    }
	  };
	}
]);
