app.controller('AdminNavCtrl', ['$scope', '$location', '$window', '$http', function($scope, $location, $window, $http) {

    $scope.activeTab = "";

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'addUsers') {
            //show add users
            $scope.activeTab = 'addUsers';
            $("#addUsersCtrlDiv").show();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").hide();
        } else if (hash == 'editUsers') {
            //show edit users
            $scope.activeTab = 'editUsers';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").show();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").hide();
        } else if (hash == 'addCosts') {
            //show add costs
            $scope.activeTab = 'addCosts';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").show();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").hide();
        } else if (hash == 'viewCosts') {
            //show edit costs
            $scope.activeTab = 'viewCosts';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").show();
            $("#addUserBulkCtrlDiv").hide();
        } else if (hash == 'addUserBulk') {
            //show edit costs
            $scope.activeTab = 'addUserBulk';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").show();
        } else if (hash == 'help') {
            //show help
            $scope.activeTab = 'help';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").show();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").hide();
        } else {
            //show summary
            $scope.activeTab = 'requestDashboard';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").show();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").hide();
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
