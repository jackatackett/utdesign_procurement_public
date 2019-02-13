app.controller('CreateRequestCtrl', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {

    var fieldKeys = ["description", "partNo", "quantity", "unitCost"];
    $scope.fields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost"];
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

    //add a row when the thing loads
    $timeout($scope.addRow, 0);
}]);