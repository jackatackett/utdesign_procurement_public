app.controller('AdminEditCosts', ['$scope', '$location', '$http', '$timeout', '$interval', 'costTypeLut', function($scope, $location, $http, $timeout, $interval, costTypeLut) {

    $scope.costTypeLut = costTypeLut;

    function convertCosts(value) {
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
    };

    $scope.fieldKeys = ["timestamp", "projectNumber", "type", "amount", "comment", "actor"];
    $scope.fields = ["Timestamp", "Project Number", "Type", "Amount", "Comment", "Assigned by"];

    $scope.costs = [];
    $scope.getCosts = function(e) {
        $http.post('/getCosts', {}).then(function(resp) {
            $scope.costs = cleanData(resp.data);
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
        });
    };

    $timeout($scope.getCosts, 0);
    $interval($scope.getCosts, 5000);

}]);
