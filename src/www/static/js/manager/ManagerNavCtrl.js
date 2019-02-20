app.controller('ManagerNavCtrl', ['$scope', '$location', function($scope, $location) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'viewRequests') {
            //show status
            $("#viewRequestsCtrlDiv").show();
            $("#managerHelpDiv").hide();

        } else {
            //show help
            $("#viewRequestsCtrlDiv").hide();
            $("#managerHelpDiv").show();
        }

        console.log("manager stuff", $location.hash());
    });

}]);