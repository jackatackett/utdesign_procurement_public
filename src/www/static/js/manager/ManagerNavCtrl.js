app.controller('ManagerNavCtrl', ['$scope', '$location', '$window', '$http', function($scope, $location, $window, $http) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();
        $scope.activeTab = "";

        if (hash == 'help') {
            //show help
            $scope.activeTab = 'help';
            $("#viewRequestsCtrlDiv").hide();
            $("#viewBudgetDiv").hide();
            $("#managerHelpDiv").show();
        }
        else if (hash == 'budget') {
            //show status
            $scope.activeTab = 'budget';
            $("#viewRequestsCtrlDiv").hide();
            $("#viewBudgetDiv").show();
            $("#managerHelpDiv").hide();
        }
        else {
            //show help
            $scope.activeTab = 'requestDashboard';
            $("#viewRequestsCtrlDiv").show();
            $("#viewBudgetDiv").hide();
            $("#managerHelpDiv").hide();
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
