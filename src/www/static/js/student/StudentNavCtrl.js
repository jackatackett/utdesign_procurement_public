app.controller('StudentNavCtrl', ['$scope', '$location', function($scope, $location) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'create') {
            //show create
            $("#createRequestCtrlDiv").show();
            $("#requestSummaryCtrlDiv").hide();
            $("#studentHelpDiv").hide();

        } else if (hash == 'status') {
            //show status
            $("#createRequestCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").show();
            $("#studentHelpDiv").hide();

        } else {
            //show help
            $("#createRequestCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#studentHelpDiv").show();
        }

        console.log("moo", $location.hash());
    });

}]);