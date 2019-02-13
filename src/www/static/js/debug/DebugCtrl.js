app.controller('DebugCtrl', ['$scope', '$http', '$sce', function($scope, $http, $sce) {

    $scope.data = "Input goes here";
    $scope.output = "Output goes here";
    $scope.url = "/api/procurementRequest";
    $scope.status = "#FFF"
    $scope.showHTML = false;

    $scope.makeRequest = function() {
        console.log("makeRequest", $scope.data);
        $http.post($scope.url, $scope.data).then(function(data) {
            console.log(data);
            $scope.status = "green";
            $scope.output = JSON.stringify(data);
            $scope.showHTML = false;
        }, function(err) {
            console.log(err);
            $scope.status = "red";
            $scope.output = $sce.trustAsHtml(err.data);
            $scope.showHTML = true;
        });
    }

}]);