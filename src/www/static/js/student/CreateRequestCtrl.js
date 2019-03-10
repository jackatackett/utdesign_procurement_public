app.controller('CreateRequestCtrl', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {

    $scope.errorText = "";
    $scope.projectNumbers = [];
    $scope.fieldKeys = ["description", "partNo", "quantity", "unitCost", "totalCost"];
    $scope.fields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.request = {
        vendor: '',
        URL: '',
        projectNumber: -1,
        items: []
    };

    /**
        Adds a new item to the $scope.request.items list.
    */
    $scope.addRow = function() {
        $scope.request.items.push(newRow());
    }

    /**
        Removes a specific item from the $scope.request.items list.
    */
    $scope.deleteRow = function(rowIdx) {
        $scope.request.items.splice(rowIdx, 1);
    }

    /**
        Submits $scope.request to the /procurementRequest REST endpoint
        if the $scope.request is valid.
    */
    $scope.makeRequest = function() {

        // validate and format the request
        if (!validateRequest()) {
            return;
        }
        formatRequest();

        // send the request to the REST endpoint
        $http.post('/procurementRequest', $scope.request).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
        }, function(err) {
            console.error("Error", err.data)
            alert("Error");
        });
    }

    /**
        Verifies that $scope.request is valid but does not mutate it
    */
    function validateRequest() {

        if ($scope.projectNumbers.indexOf($scope.request.projectNumber) < 0) {
            $scope.errorText = "Invalid Project Number";
            return false;
        }

        if ($scope.request.vendor.trim().length <= 0) {
            $scope.errorText = "Vendor must not be empty";
            return false;
        }

        if ($scope.request.URL.trim().length <= 0) {
            $scope.errorText = "Vendor URL must not be empty";
            return false;
        }

        for (var x = 0; x < $scope.request.items.length; x++) {
            var item = $scope.request.items[x];

            //no empty description
            if (!item.description || item.description.trim().length == 0) {
                $scope.errorText = "Description should not be empty in item " + (x+1);
                return false;
            }

            //no empty partNo
            if (!item.partNo || item.partNo.trim().length == 0) {
                $scope.errorText = "Part number should not be empty in item " + (x+1);
                return false;
            }

            //quantity must be integer
            if (!Number.isInteger(+item.quantity)) {
                $scope.errorText = "Quantity should be an integer in item " + (x+1);
                return false;
            }

            //unitCost must be at most 2 past the decimal
            if (!item.unitCost || Math.abs(Math.round(item.unitCost*100) - item.unitCost*100) >= .1) {
                $scope.errorText = "Unit cost should be a dollar amount in item " + (x+1);
                return false;
            }
        }

        $scope.errorText = "";
        return true;
    }

    /**
        Modifies $scope.request to fit the format that /procurementRequest
        expects.
    */
    function formatRequest() {
        // convert projectNumber to Number
        $scope.request.projectNumber = +$scope.request.projectNumber;

        // convert all quantity amounts to Number
        for (var x = 0; x < $scope.request.items.length; x++) {
            var item = $scope.request.items[x];
            item.quantity = +item.quantity;
        }
    }

    /**
        Updates $scope.request.items[*].totalCost to be quantity*unitCost
        for a given row.
    */
    $scope.updateCost = function(rowIdx) {
        var item = $scope.request.items[rowIdx];
        item.totalCost = (item.quantity * item.unitCost).toFixed(2);
    }

    /**
        Returns an empty item object
    */
    function newRow() {
        var ret = {};
        for (var x = 0; x < $scope.fields.length; x++) {
            ret[$scope.fields[x]] = "";
        }
        return ret;
    }

    //add a row when the thing loads
    $timeout($scope.addRow, 0);

    //get the project numbers associated with this user
    $http.post('/userProjects').then(function(resp) {
        $scope.projectNumbers = resp.data;
        if ($scope.projectNumbers.length > 0) {
            $scope.selectedProject = $scope.projectNumbers[0];
        }
    }, function(err) {
        console.error(err);
    });

}]);