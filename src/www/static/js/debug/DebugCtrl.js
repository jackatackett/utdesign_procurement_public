app.controller('DebugCtrl', ['$scope', '$http', '$sce', function($scope, $http, $sce) {

    $scope.data = "Input goes here";
    $scope.output = "Output goes here";
    $scope.url = "/procurementRequest";
    $scope.status = "#FFF"
    $scope.showHTML = false;

    $scope.makeRequest = function() {
        $http.post($scope.url, $scope.data).then(function(data) {
            $scope.status = "green";
            $scope.output = JSON.stringify(data.data);
            $scope.showHTML = false;
        }, function(err) {
            $scope.status = "red";
            $scope.output = $sce.trustAsHtml(err.data);
            $scope.showHTML = true;
        });
    }

}]);