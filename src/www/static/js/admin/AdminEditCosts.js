app.controller('AdminEditCosts', ['$scope', '$location', '$http', '$timeout', '$interval', function($scope, $location, $http, $timeout, $interval) {

    function convertCosts(value) {
        console.log(value);
        if (typeof value === "undefined") {
            return "$0.00";
        }
        value = String(value);
        if (value !== "undefined") {
            while (value.length < 3) {
                value = "0" + value;
            }
            return "$" + value.slice(0, -2) + "." + value.slice(value.length-2);
        }
        return "$0.00"
    };

    function cleanData(data) {
        var result = [];
        for (var d in data) {
            result[d] = data[d];
            result[d]["amount"] = convertCosts(data[d]["amount"]);
        }
        return result;
    }

    $scope.fieldKeys = ["projectNumber", "type", "amount", "comment", "actor"];
    $scope.fields = ["Project Number", "Type", "Amount", "Comment", "Assigned by"];

    $scope.costs = [];
    $scope.getCosts = function(e) {
        $http.post('/getCosts', {}).then(function(resp) {
            console.log("Success", resp);
            $scope.costs = cleanData(resp.data);
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
        });
    };

    $timeout($scope.getCosts, 0);
    $interval($scope.getCosts, 5000);

    //~ $scope.selectedCost = {};

    //~ $scope.editCost = function(e, rowIdx) {
        //~ $("#editCostModal").show();
        //~ $scope.selectedCost = {};
        //~ var co = $scope.costs[rowIdx];
        //~ for (var key in co) {
            //~ if (co.hasOwnProperty(key)) {
                //~ $scope.selectedCost[key] = co[key];
            //~ }
        //~ }
    //~ };

    //~ $scope.closeEditBox = function(e) {
        //~ $("#editCostModal").hide();
    //~ };

    //~ $scope.errorText = "";

    //~ function validateInput() {
        //~ console.log("validating input");
        //~ for (var inputKey in $scope.fieldKeys) {
            //~ var value = $("#newCost" + $scope.fieldKeys[inputKey]).val();
            //~ console.log(inputKey, value);
            //~ if (value.trim().length <= 0) {
                //$scope.errorText = "Field " + $("#newCost" + $scope.fieldKeys[inputKey]).parent().prev().html() + " should not be empty";
                //~ $scope.errorText = "Field " + $scope.fields[inputKey] + " should not be empty";
                //~ return false;
            //~ }
            //~ //project number must be integer
            //~ if ($scope.fieldKeys[inputKey] == "projectNumber" && !Number.isInteger(+$scope.fieldKeys[inputKey])) {
                //~ $scope.errorText = "Project Number should be an integer";
                //~ return false;
            //~ }
            //~ //amount must be at most 2 past the decimal
            //~ if ($scope.fieldKeys[inputKey] == "amount" && Math.abs(Math.round($scope.fieldKeys[inputKey]*100) - $scope.fieldKeys[inputKey]*100) >= .1) {
                //~ $scope.errorText = "Amount should be a dollar amount";
                //~ return false;
            //~ }
            //~ //type must be either: refund, reimbursement, funding
        //~ }
        //~ $scope.errorText = "";
        //~ return true;
    //~ };

    //~ $scope.saveCostEdit = function() {
        //~ //need to validate input
        //~ if (validateInput()) {
            //~ //post and update
            //~ $("#editCostModal").hide();
        //~ }
    //~ }

}]);
