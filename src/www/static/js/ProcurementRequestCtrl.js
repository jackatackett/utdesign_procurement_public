app.controller('ProcurementRequestCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.fields = ["Description", "URL", 'Vendor', "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total"];
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