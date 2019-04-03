app.controller('RequestSummaryCtrl', ['$scope', '$http', '$location', '$timeout', '$interval', 'dispatcher', function($scope, $http, $location, $timeout, $interval, dispatcher) {

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

    $scope.fieldKeys = ["requestNumber", "projectNumber", "manager", "status", "vendor", "URL", "justification", "additionalInfo"];
    $scope.fields = ["Request Number", "Project Number", "Assigned Manager Email", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "itemURL", "partNo", "quantity", "unitCost", "totalCost"];
    $scope.itemFields = ["Description", "Item URL", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];

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
                        status: "approved",
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

    $scope.editRequest = function(request) {
        dispatcher.emit('editRequest', request);
        $location.hash('create');
    }

    $scope.cloneRequest = function(request) {
        dispatcher.emit('cloneRequest', request);
        $location.hash('create');
    }

    $scope.cancelRequest = function(request) {
        if (request._id) {
            $http.post('/procurementCancel', {_id: request._id}).then(function(resp) {
                console.log(resp);
                alert("Success!");
                $scope.refreshStatuses();
            }, function(err) {
                console.error(err);
                alert("Error!");
                $scope.refreshStatuses();
            })
        } else {
            console.error("Cancel Request cannot proceed without _id. See:", request);
            alert("Cancel Request cannot proceed without _id.");
        }
    }

    $scope.canEdit = function(status) {
        return status == "saved" || status == "updates for manager" || status == "updates for admin";
    }

    $scope.refreshStatuses = function() {
        $http.post('/procurementStatuses', {}).then(function(resp) {
            console.log("procurementStatuses success", resp)
            $scope.data = cleanData(resp.data);
        }, function(err) {
            console.error("Error", err.data)
        });
    }

    $timeout($scope.refreshStatuses, 0);
    $interval($scope.refreshStatuses, 5000);

    dispatcher.on("refreshStatuses", $scope.refreshStatuses);

    $scope.historyFields = ["Timestamp", "Source", "Comment", "Old State", "New State"];
    $scope.historyFieldKeys = ["timestamp", "actor", "comment", "oldState", "newState"];

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
