app.controller('ProcurementRequestCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.fields = ["Description", "URL", 'Vendor', "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total"];
    $scope.grid = [];

    $scope.addRow = function() {
        $scope.grid.push(newRow());
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