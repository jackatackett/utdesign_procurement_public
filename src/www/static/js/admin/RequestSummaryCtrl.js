app.controller('RequestSummaryCtrl', ['$scope', '$location', '$http', '$timeout', '$interval', function($scope, $location, $http, $timeout, $interval) {
    function convertCosts(value) {
//        console.log(value);
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
            for (var item in data[d]["items"]) {
                result[d]["items"][item]["unitCost"] = convertCosts(data[d]["items"][item]["unitCost"]);
                result[d]["items"][item]["totalCost"] = convertCosts(data[d]["items"][item]["totalCost"]);
            }
        }
        return result;
    };

    $scope.fieldKeys = ["requestNumber", "projectNumber", "status", "vendor", "URL", "justification", "additionalInfo"];
    $scope.fields = ["Request Number", "Project Number", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", 'itemURL', "partNo", "quantity", "unitCost", "totalCost"];
    $scope.itemFields = ["Description", 'Item URL', "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.teams = ["Procurement", "Clock-It", "Smart Glasses"];
//~ <<<<<<< HEAD
    //~ $scope.statuses = ["Pending", "Accepted", "Rejected", "Shipped", "Canceled"];
    $scope.filters = ["Project Number", "Vendor"];
    $scope.historyFields = ["Timestamp", "Source", "Comment", "Old State", "New State"];
    $scope.historyFieldKeys = ["timestamp", "actor", "comment", "oldState", "newState"];
//~ =======
    $scope.statuses = ["Pending", "Saved", "Manager Approved", "Admin Approved", "Rejected", "Updates for Manager", "Updates for Admin", "Cancelled", "Ordered", "Ready for Pickup", "Complete"];
    $scope.statusesKeys = ["pending", "saved", "manager approved", "admin approved", "rejected", "updates for manager", "updates for admin", "cancelled", "ordered", "ready for pickup", "complete"];
//~ >>>>>>> dd34bbafb14100851e50535618cc3e625721348e

    $scope.filters = ["Project Number", "Vendor"];
    $scope.filterKeys = ["projectNumbers", "vendor"];
    $scope.filterValues = {};
    $scope.tableFilters = {};

    $scope.data = [];

    $scope.adminComment = "";

    $scope.selectedStatuses = [];
    $scope.addToSelectedStatuses = function(status) {
        if ($scope.selectedStatuses.includes(status)) {
            var idx = $scope.selectedStatuses.indexOf(status);
            if (idx !== -1) $scope.selectedStatuses.splice(idx, 1);
        } else {
            $scope.selectedStatuses.push(status);
        }
    };

    $scope.expanded = false;
    $scope.showCheckboxes = function() {
        var checkboxes = document.getElementById("checkboxes");
        if (!$scope.expanded) {
            checkboxes.style.display = "block";
            $scope.expanded = true;
        } else {
            checkboxes.style.display = "none";
            $scope.expanded = false;
        }
    }

    $scope.toggleCollapse = function(e) {
        var target = e.currentTarget;
        $(target.nextElementSibling).toggle();
    };

    $scope.regenerateTable = function(e) {

        var filters = {};
        for (var f in $scope.filterKeys) {
            if ($scope.filterValues[$scope.filterKeys[f]] && $scope.filterValues[$scope.filterKeys[f]].length > 0) {
                if ($scope.filterKeys[f] == "projectNumbers") {
                    filters[$scope.filterKeys[f]] = Number($scope.filterValues[$scope.filterKeys[f]]);
                } else {
                    filters[$scope.filterKeys[f]] = $scope.filterValues[$scope.filterKeys[f]];
                }
            }
        }
        if ($scope.selectedStatuses.length > 0) {
            filters.statuses = $scope.selectedStatuses;
        }

        $scope.tableFilters = filters;

        $http.post('/procurementStatuses', $scope.tableFilters).then(function(resp) {
            $scope.data = resp.data;
        }, function(err) {
            console.error("Error", err.data)
        });
    };

    $scope.rejectRequest = function(e, rowIdx) {
        $scope.adminComment = "";
        $("#rejectModal").show();
        currentRow = rowIdx;
    };

    $scope.permanentReject = function(e) {
        $http.post('/procurementRejectAdmin', {'_id':$scope.data[currentRow]._id, "comment": $scope.adminComment}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.adminComment = "";
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.adminComment = "";
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        });
    };

    $scope.sendForUpdatesAdmin = function(e) {
        $http.post('/procurementUpdateAdmin', {'_id':$scope.data[currentRow]._id, "comment": $scope.adminComment}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.adminComment = "";
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.adminComment = "";
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        });
    };

    $scope.sendForUpdatesManagerAdmin = function(e) {
        $http.post('/procurementUpdateManagerAdmin', {'_id':$scope.data[currentRow]._id, "comment": $scope.adminComment}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.adminComment = "";
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.adminComment = "";
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        });
    };

    $scope.closeRejectBox = function(e) {
        $scope.adminComment = "";
        $("#rejectModal").hide();
    };

    $scope.setShipping = function(e) {
        $http.post('/procurementOrder', {'_id':$scope.data[shippingRow]._id, "amount":$("#shippingAmt").val()}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.refreshStatuses();
            $scope.cancelShippingBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.refreshStatuses();
            $scope.cancelShippingBox();
        });
    }

    $scope.cancelShippingBox = function(e) {
        $("#shippingModal").hide();
    };

    $scope.orderRequest = function(e, rowIdx) {
        console.log($scope.data);
        console.log(rowIdx);
        shippingRow = rowIdx;
        $("#shippingModal").show();
        
    };

    $scope.readyRequest = function(e, rowIdx) {
        console.log($scope.data);
        console.log(rowIdx);
        $http.post('/procurementReady', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.refreshStatuses();
        }, function(err) {
            console.error("Error", err.data)
            alert("Error");
            $scope.refreshStatuses();
        });
    };

    $scope.completeRequest = function(e, rowIdx) {
        console.log($scope.data);
        console.log(rowIdx);
        $http.post('/procurementComplete', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.refreshStatuses();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.refreshStatuses();
        });
    };

    $scope.canOrder = function(status) {
        return status == "manager approved";
    };

    $scope.canPickup = function(status) {
        return status == "ordered";
    };

    $scope.canComplete = function(status) {
        return status == "ready for pickup";
    };

    $scope.refreshStatuses = function() {
        if ($scope.tableFilters.statuses && $scope.tableFilters.statuses.length < 1) {
            delete $scope.tableFilters.statuses;
        }

        $http.post('/procurementStatuses', $scope.tableFilters).then(function(resp) {
            $scope.data = cleanData(resp.data);
        }, function(err) {
            console.error("Error", err.data)
        });
    }

    $timeout($scope.refreshStatuses, 0);
    $interval($scope.refreshStatuses, 5000);

    $scope.viewHistory = function(e, rowIdx) {
        console.log("history");
        //~ console.log($scope.data[rowIdx]);
        //~ console.log($scope.data[rowIdx]["history"]);
        $("#historyBody").empty();
        var historyHTML = "";
        for (var hist in $scope.data[rowIdx]["history"]) {
            historyHTML += '<tr style="border-bottom: 1.5px solid black">';
                //~ console.log($scope.data[rowIdx]["history"][hist]);
            for (var ele in $scope.historyFieldKeys) {
                historyHTML += '<td scope="col" style="background-color: #eee;">' + $scope.data[rowIdx]["history"][hist][$scope.historyFieldKeys[ele]] + '</td>';
            }
            historyHTML += '</tr>';
        }
        if (historyHTML == "") {
            historyHTML = "No history";
        }
        $("#historyBody").append(historyHTML);
        console.log(historyHTML);
        $("#historyModal").show();
    };

    $scope.closeHistoryBox = function(e) {
        $("#historyModal").hide();
    };

}]);
