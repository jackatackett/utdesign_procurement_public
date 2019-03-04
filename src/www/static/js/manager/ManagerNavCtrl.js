app.controller('ManagerNavCtrl', ['$scope', '$location', function($scope, $location) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'viewRequests') {
            //show status
            $("#viewRequestsCtrlDiv").show();
            $("#viewBudgetDiv").hide();
            $("#managerHelpDiv").hide();
        }
        else if (hash == 'budget') {
            //show status
            $("#viewRequestsCtrlDiv").hide();
            $("#viewBudgetDiv").show();
            $("#managerHelpDiv").hide();
        }
        else {
            //show help
            $("#viewRequestsCtrlDiv").hide();
            $("#viewBudgetDiv").hide();
            $("#managerHelpDiv").show();
        }

        console.log("manager stuff", $location.hash());
    });

}]);
