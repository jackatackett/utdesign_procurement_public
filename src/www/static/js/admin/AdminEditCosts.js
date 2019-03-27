app.controller('AdminEditCosts', ['$scope', '$location', '$http', '$timeout', '$interval', function($scope, $location, $http, $timeout, $interval) {

    $scope.fieldKeys = ["projectNumber", "type", "amount", "comment", "actor"];
    $scope.fields = ["Project Number", "Type", "Amount", "Comment", "Assigned by"];

    $scope.costs = [];
    $scope.getCosts = function(e) {
        $http.post('/getCosts', {}).then(function(resp) {
            console.log("Success", resp);
            $scope.costs = resp.data;
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
        });
    };

    $timeout($scope.getCosts, 0);
    $interval($scope.getCosts, 5000);

    $scope.selectedCost = {};

    $scope.editCost = function(e, rowIdx) {
        $("#editCostModal").show();
        $scope.selectedCost = {};
        var co = $scope.costs[rowIdx];
        for (var key in co) {
            if (co.hasOwnProperty(key)) {
                $scope.selectedCost[key] = co[key];
            }
        }
    };

    $scope.closeEditBox = function(e) {
        $("#editCostModal").hide();
    };

    $scope.errorText = "";

    function validateInput() {
        console.log("validating input");
        for (var inputKey in $scope.fieldKeys) {
            var value = $("#newCost" + $scope.fieldKeys[inputKey]).val();
            console.log(inputKey, value);
            if (value.trim().length <= 0) {
                //~ $scope.errorText = "Field " + $("#newCost" + $scope.fieldKeys[inputKey]).parent().prev().html() + " should not be empty";
                $scope.errorText = "Field " + $scope.fields[inputKey] + " should not be empty";
                return false;
            }
            //project number must be integer
            if ($scope.fieldKeys[inputKey] == "projectNumber" && !Number.isInteger(+$scope.fieldKeys[inputKey])) {
                $scope.errorText = "Project Number should be an integer";
                return false;
            }
            //amount must be at most 2 past the decimal
            if ($scope.fieldKeys[inputKey] == "amount" && Math.abs(Math.round($scope.fieldKeys[inputKey]*100) - $scope.fieldKeys[inputKey]*100) >= .1) {
                $scope.errorText = "Amount should be a dollar amount";
                return false;
            }
            //type must be either: refund, reimbursement, funding
        }
        $scope.errorText = "";
        return true;
    };

    $scope.saveCostEdit = function() {
        //need to validate input
        if (validateInput()) {
            //post and update
            $("#editCostModal").hide();
        }
    }

}]);
