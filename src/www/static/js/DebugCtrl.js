app.controller('DebugCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.data = "Input goes here";
    $scope.output = "Output goes here";
    $scope.url = "procurementRequest";
    $scope.status = "#FFF"

    $scope.makeRequest = function() {
        console.log("makeRequest", $scope.data);
        $http.post($scope.url, $scope.data).then(function(data) {
            console.log(data);
            $scope.status = "green";
            $scope.output = JSON.stringify(data);
        }, function(err) {
            console.log(err);
            $scope.status = "red";
            $scope.output = "Error: " + JSON.stringify(err);
        });
    }

}]);