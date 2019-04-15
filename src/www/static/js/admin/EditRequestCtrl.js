app.controller('EditRequestCtrl', ['$scope', '$http', '$timeout', 'dispatcher', function($scope, $http, $timeout, dispatcher) {

    $scope.errorText = "";
    $scope.projectNumbers = [];
    $scope.projectManagers = [];
    $scope.fieldKeys = ["description", "itemURL", "partNo", "quantity", "unitCost", "totalCost"];
    $scope.fields = ["Description", "Item URL", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
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
        Saves $scope.request with the /procurementSave REST endpoint
        with the submit flag False.

        If the $scope.request is invalid, a warning is shown and the
        request is not submitted.
    */
    $scope.saveRequest = function(submit) {

        // validate and format the request
        if (!validateRequest()) {
            return;
        }
        formatRequest();

        $http.post("/procurementSave", $scope.request).then(function(resp) {
            alert("Success!");
            dispatcher.emit("refreshStatuses");
            $scope.closeEditBox();
        }, function(err) {
            $scope.errorText = "Infrastructure error. Please refresh page. Contact staff if problem persists.";
            console.error(err);
        });
    };

    /**
        Verifies that $scope.request is valid but does not mutate it
    */
    function validateRequest() {

        if ($scope.request.vendor.trim().length <= 0) {
            $scope.errorText = "Vendor must not be empty";
            return false;
        }

        if ($scope.request.URL.trim().length <= 0) {
            $scope.errorText = "Vendor URL must not be empty";
            return false;
        }

        if (!$scope.request.shippingCost || Math.abs(Math.round($scope.request.shippingCost*100) - $scope.request.shippingCost*100) >= .1) {
            $scope.errorText = "Shipping cost should be a dollar amount";
            return false;
        }

        for (var x = 0; x < $scope.request.items.length; x++) {
            var item = $scope.request.items[x];

            //no empty description
            if (!item.description || item.description.trim().length == 0) {
                $scope.errorText = "Description should not be empty in item " + (x+1);
                return false;
            }

            //no empty description
            if (!item.itemURL || item.itemURL.trim().length == 0) {
                $scope.errorText = "Item URL should not be empty in item " + (x+1);
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

        $scope.request["adminEdit"] = true;
    }

    /**
        Updates $scope.request.items[*].totalCost to be quantity*unitCost
        for a given row.
    */
    $scope.updateCost = function(rowIdx) {
        var item = $scope.request.items[rowIdx];
        if (item.unitCost == undefined || item.quantity == undefined)
            item.totalCost = "";
        else
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

    $scope.newRequest = function() {
        $scope.request = {
            vendor: '',
            URL: '',
            projectNumber: -1,
            items: []
        };
        $scope.addRow();
    };

    dispatcher.on('editRequest', function() {
        //deep copy the request
        $scope.request = JSON.parse(JSON.stringify($scope.selectedRequestInfo));

        //remove the dollar signs on unit and total cost
        // TODO Find out if this is actually necessary
        if ($scope.request['shippingCost']) {
            if ($scope.request['shippingCost'].replace) {
                $scope.request["shippingCost"] = $scope.request["shippingCost"].replace("$", "");
            }

            for (var x in $scope.request["items"]) {
                if ($scope.request["items"][x]["unitCost"].replace) {
                    $scope.request["items"][x]["unitCost"] = $scope.request["items"][x]["unitCost"].replace("$", "");
                }

                if ($scope.request["items"][x]["totalCost"].replace) {
                    $scope.request["items"][x]["totalCost"] = $scope.request["items"][x]["totalCost"].replace("$", "");
                }
            }
        }
        //~ $scope.refreshManagers();
    });

    $scope.closeEditBox = function(e) {
        $("#requestEditModal").hide();
    };

}]);
