app.controller('AdminNavCtrl', ['$scope', 'dispatcher', '$timeout', '$location', '$window', '$http', function($scope, dispatcher, $timeout, $location, $window, $http) {

    $scope.activeTab = "";
    $scope.showBulkAdd = false;

    dispatcher.on('bulkRefresh', function() {
        $timeout(function() {$scope.showBulkAdd = true;}, 0);
    });

    dispatcher.on('bulkEnd', function() {
        $timeout(function() {$scope.showBulkAdd = false;}, 0);
    });

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
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").hide();
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
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").hide();
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
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").hide();
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
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").hide();
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
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").hide();
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
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").hide();
        } else if (hash == 'addProjects') {
            //show addProjects
            $scope.activeTab = 'addProjects';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").hide();
            $("#addProjectsCtrlDiv").show();
            $("#editProjectsCtrlDiv").hide();
        } else if (hash == 'editProjects') {
            //show editProjects
            $scope.activeTab = 'editProjects';
            $("#addUsersCtrlDiv").hide();
            $("#editUsersCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#adminHelpDiv").hide();
            $("#adminAddCostsDiv").hide();
            $("#adminEditCostsDiv").hide();
            $("#addUserBulkCtrlDiv").hide();
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").show();
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
            $("#addProjectsCtrlDiv").hide();
            $("#editProjectsCtrlDiv").hide();
        }
    });

    $scope.doLogout = function() {
        $http.post('/userLogout').then(function(resp) {
            $window.location.href = '/login';
        }, function(err) {
            $window.location.href = '/login';
        });
    };

}]);
