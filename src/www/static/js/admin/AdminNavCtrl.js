app.controller('AdminNavCtrl', ['$scope', '$location', '$window', '$http', function($scope, $location, $window, $http) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'requestSummary') {
            //show summary
            $("#addUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").show();
            $("#adminHelpDiv").hide();

        } else if (hash == 'addUsers') {
            //show add users
            $("#addUsersCtrlDiv").show();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();

        } else {
            //show help
            $("#addUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").show();
        }

        console.log("admin stuff", $location.hash());
    });

    $scope.doLogout = function() {
        $http.post('/userLogout').then(function(resp) {
            $window.location.href = '/login';
        }, function(err) {
            console.err("Fatal error logging out:", err);
        });
    };

}]);