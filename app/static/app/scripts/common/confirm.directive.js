'use strict';

angular.module('mango')
.directive('confirmDelete', [
	function() {
		return {
			// scope: {
			// 	title: '='
			// },
			link: function (scope, element, attr) {
				element.bind('click',function (event) {
					event.stopPropagation();
					var msg = "Are you sure you want to delete \"" + scope.$eval(attr.title) + "\"?";
					var clickAction = attr.confirmedClick;
					if ( window.confirm(msg) ) {
						scope.$eval(clickAction);
					}
				});
			}
		};
	}
]);