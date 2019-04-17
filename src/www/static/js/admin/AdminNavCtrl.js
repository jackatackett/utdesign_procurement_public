app.controller('AdminNavCtrl', ['$scope', 'dispatcher', '$timeout', '$location', '$window', '$http', function($scope, dispatcher, $timeout, $location, $window, $http) {

    $scope.activeTab = "";
    $scope.activeId = "";
    $scope.showBulkAdd = false;
    $scope.tabIds = [
        "#addUsersCtrlDiv",
        "#editUsersCtrlDiv",
        "#requestSummaryCtrlDiv",
        "#adminHelpDiv",
        "#adminAddCostsDiv",
        "#adminEditCostsDiv",
        "#addUserBulkCtrlDiv",
        "#addProjectsCtrlDiv",
        "#editProjectsCtrlDiv",
    ];

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
            $scope.activeTab = 'addUsers';
            $scope.activeId = "#addUsersCtrlDiv";
        } else if (hash == 'editUsers') {
            $scope.activeTab = 'editUsers';
            $scope.activeId = "#editUsersCtrlDiv";
        } else if (hash == 'addCosts') {
            $scope.activeTab = 'addCosts';
            $scope.activeId = "#adminAddCostsDiv";
        } else if (hash == 'viewCosts') {
            $scope.activeTab = 'viewCosts';
            $scope.activeId = "#adminEditCostsDiv";
        } else if (hash == 'addUserBulk') {
            $scope.activeTab = 'addUserBulk';
            $scope.activeId = "#addUserBulkCtrlDiv";
        } else if (hash == 'help') {
            $scope.activeTab = 'help';
            $scope.activeId = "#adminHelpDiv";
        } else if (hash == 'addProjects') {
            $scope.activeTab = 'addProjects';
            $scope.activeId = "#addProjectsCtrlDiv";
        } else if (hash == 'editProjects') {
            $scope.activeTab = 'editProjects';
            $scope.activeId = "#editProjectsCtrlDiv";
        } else {
            $scope.activeTab = 'requestDashboard';
            $scope.activeId = "#requestSummaryCtrlDiv";
        }

        $scope.tabIds.forEach(function(tabId) {
            if (tabId == $scope.activeId) {
                $(tabId).show();
            } else {
                $(tabId).hide();
            }
        })
    });

    $scope.doLogout = function() {
        $http.post('/userLogout').then(function(resp) {
            $window.location.href = '/login';
        }, function(err) {
            $window.location.href = '/login';
        });
    };

}]);
