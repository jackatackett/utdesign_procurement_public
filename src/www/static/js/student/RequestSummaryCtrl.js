app.controller('RequestSummaryCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.fields = ["Group ID", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];

    $scope.addRow = function() {
        $scope.grid.push(newRow());
    }

    $scope.makeRequest = function() {
        console.log("makeRequest", $scope.grid);
        $http.post('/procurementRequest', $scope.grid, function(data) {
            console.log("Success", data)
        }, function(err) {
            console.error("Error", err)
        })
    }

    function newRow() {
        var ret = {};
        for (var x = 0; x < $scope.fields.length; x++) {
            ret[$scope.fields[x]] = "";
        }
        return ret;
    }

    $(document).ready(function() {
        $scope.addRow();
    });
}]);