app.controller('StudentNavCtrl', ['$scope', '$location', '$window', '$http', function($scope, $location, $window, $http) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

        if (hash == 'create') {
            //show create
            $scope.activeTab = 'createRequest';
            $("#createRequestCtrlDiv").show();
            $("#requestSummaryCtrlDiv").hide();
            $("#studentHelpDiv").hide();
            $("#viewBudgetDiv").hide();
        } else if (hash == 'budget') {
            //show budget
            $scope.activeTab = 'budget';
            $("#createRequestCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#studentHelpDiv").hide();
            $("#viewBudgetDiv").show();
        } else if (hash == 'help') {
            //show help
            $scope.activeTab = 'help';
            $("#createRequestCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").hide();
            $("#studentHelpDiv").show();
            $("#viewBudgetDiv").hide();
        } else {
            //show status
            $scope.activeTab = 'requestDashboard';
            $("#createRequestCtrlDiv").hide();
            $("#requestSummaryCtrlDiv").show();
            $("#studentHelpDiv").hide();
            $("#viewBudgetDiv").hide();
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
