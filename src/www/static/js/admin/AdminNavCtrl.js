app.controller('AdminNavCtrl', ['$scope', '$location', '$window', '$http', function($scope, $location, $window, $http) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'requestSummary') {
            //show summary
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").show();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
        } else if (hash == 'addUsers') {
            //show add users
            $("#addUsersCtrlDiv").show();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
        } else if (hash == 'editUsers') {
            //show edit users
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").show();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
        } else if (hash == 'addCosts') {
            //show add costs
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").show();
            $("#adminEditCostsDiv").hide();
        } else if (hash == 'viewCosts') {
            //show edit costs
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").show();
        } else {
            //show help
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").show();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
        }

        console.log("admin stuff", $location.hash());
    });

    $scope.doLogout = function() {
        $http.post('/userLogout').then(function(resp) {
            $window.location.href = '/login';
        }, function(err) {
            $window.location.href = '/login';
        });
    };

}]);
