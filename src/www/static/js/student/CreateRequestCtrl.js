app.controller('CreateRequestCtrl', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {

    $scope.fieldKeys = ["description", "partNo", "quantity", "unitCost", "totalCost"];
    $scope.fields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.grid = [];
    $scope.metadata = {};

    $scope.addRow = function() {
        $scope.grid.push(newRow());
    }

    $scope.makeRequest = function() {
        console.log("makeRequest", $scope.grid);

        //TODO validate the data

        //TODO don't alias like a moron
        var data = $scope.metadata;
        data['items'] = $scope.grid;

        //TODO use the SAML token and not this nonsense
        data.token = 'goose';
        data.groupID = 'group7';



        $http.post('/procurementRequest', data).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
        }, function(err) {
            console.error("Error", err.data)
            alert("Error");
        });
    }

    $scope.updateCost = function(rowIdx) {
        var item = $scope.grid[rowIdx];
        item.totalCost = item.quantity * item.unitCost;
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