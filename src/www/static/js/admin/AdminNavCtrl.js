app.controller('AdminNavCtrl', ['$scope', '$location', function($scope, $location) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'requestSummary') {
            //show status
            $("#requestSummaryCtrlDiv").show();
            $("#adminHelpDiv").hide();

        } else {
            //show help
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").show();
        }

        console.log("admin stuff", $location.hash());
    });

}]);