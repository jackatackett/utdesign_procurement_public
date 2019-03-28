app.controller('RequestSummaryCtrl', ['$scope', '$location', '$http', '$timeout', '$interval', function($scope, $location, $http, $timeout, $interval) {
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
    $scope.statuses = ["Pending", "Accepted", "Rejected", "Shipped", "Canceled"];
    $scope.filters = ["Project Number", "Vendor"];
    $scope.historyFields = ["Timestamp", "Source", "Comment", "Old State", "New State"];
    $scope.historyFieldKeys = ["timestamp", "actor", "comment", "oldState", "newState"];

    $scope.data = [ {
                        projectNumber: 123,
                        status: "pending",
                        vendor: "Home Depot",
                        URL: "homedepot.com",
                        justification: "Because he told me toooooo",
                        additionalInfo: "He is Plankton",
                        items: [ {
                                description: "A big thing",
                                partNo: "9001",
                                quantity: "25",
                                unitCost: "1000000000",
                                total: "25000000000"
                            },
                            {
                                description: "A small thing",
                                partNo: "9002",
                                quantity: "250",
                                unitCost: "10",
                                total: "2500"
                            }
                        ]
                    },
                    {
                        projectNumber: 124,
                        status: "manager approved",
                        vendor: "The Plastic Store",
                        URL: "gmail.com",
                        justification: "O Captain, My Captain",
                        additionalInfo: "He is dead, Jim",
                        items: [ {
                                description: "A hunk of plastic",
                                partNo: "9003",
                                quantity: "1",
                                unitCost: "10",
                                total: "10"
                            }
                        ]
                    }
                  ]

    $scope.toggleCollapse = function(e) {
        var target = e.currentTarget;
        $(target.nextElementSibling).toggle();
    };

    $scope.regenerateTable = function(e) {
        var target = e.currentTarget;
        console.log("refresh admin table");
    };

    $scope.approveRequest = function(e, rowIdx) {
        console.log($scope.data);
        console.log(rowIdx);
        $http.post('/procurementApproveAdmin', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.refreshStatuses();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.refreshStatuses();
        });
    };

    $scope.rejectRequest = function(e, rowIdx) {
        $("#rejectModal").show();
        currentRow = rowIdx;
    };

    $scope.permanentReject = function(e) {
        $http.post('/procurementRejectAdmin', {'_id':$scope.data[currentRow]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        });
    };

    $scope.sendForUpdatesAdmin = function(e) {
        $http.post('/procurementUpdateAdmin', {'_id':$scope.data[currentRow]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        });
    };

    $scope.sendForUpdatesManagerAdmin = function(e) {
        $http.post('/procurementUpdateManagerAdmin', {'_id':$scope.data[currentRow]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.refreshStatuses();
            $scope.closeRejectBox();
        });
    };

    $scope.closeRejectBox = function(e) {
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

    $scope.canApprove = function(status) {
        return status == "manager approved";
    };

    $scope.canOrder = function(status) {
        return status == "admin approved";
    };

    $scope.canPickup = function(status) {
        return status == "ordered";
    };

    $scope.canComplete = function(status) {
        return status == "ready for pickup";
    };

    $scope.refreshStatuses = function() {
        $http.post('/procurementStatuses', {}).then(function(resp) {
            console.log("Success", resp)
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
