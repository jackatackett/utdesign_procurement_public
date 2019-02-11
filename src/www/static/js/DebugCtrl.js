app.controller('DebugCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.data = "Input goes here";
    $scope.output = "Output goes here";
    $scope.url = "procurementRequest";

    $scope.makeRequest = function() {
        console.log("makeRequest", $scope.data);
        $http.post($scope.url, JSON.parse($scope.data)).then(function(data) {
            console.log(data);
            $scope.output = "Success: " + JSON.stringify(data);
        }, function(err) {
            console.log(err);
            $scope.output = "Error: " + JSON.stringify(err);
        });
    }

}]);