app.controller('StudentBudgetCtrl', ['$scope', '$location', '$http', '$window', function($scope, $location, $http, $window) {
    console.log("budget");
/*
    $scope.fieldKeys = ["status", "vendor", "URL", "justification", "additionalInfo", "cost"];
    $scope.fields = ["Status", "Vendor", "URL", "Justification", "Additional Info", "Cost"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];

    $scope.maxBudget = 2000.00;             //need to pull this from a defaults list

    $scope.data = [ {
                        "vendor" : "Bunning's warehouse",
                        "URL" : "https://www.bunnings.com.au/",
                        "justification" : "They're fluffy!",
                        "status" : "pending",
                        "projectNumber" : 844,
                        "additionalInfo" : "I want them",
                        "items" : [
                            {
                                "description" : "Bunny",
                                "partNo" : "1",
                                "quantity" : 2,
                                "unitCost" : 642,
                                "totalCost" : 1284,
                                "itemURL" : "bunnyurl"
                            },
                            {
                                "description" : "Squirrel",
                                "partNo" : "2",
                                "quantity" : 1,
                                "unitCost" : 432,
                                "totalCost" : 432,
                                "itemURL" : "squirrelurl"
                            }
                        ],
                        "requestTotal" : 1716,
                        "history" : [ ]
                    },
                    {
                        "vendor" : "vendor2",
                        "URL" : "requestor2URL",
                        "justification" : "",
                        "status" : "approved",
                        "projectNumber" : 844,
                        "additionalInfo" : "",
                        "items" : [
                            {
                                "description" : "item1",
                                "partNo" : "part2",
                                "quantity" : 3,
                                "unitCost" : 600,
                                "totalCost" : 900,
                                "itemURL" : "item1url"
                            }
                        ],
                        "requestTotal" : 900,
                        "history" : [
                            {
                                "actor" : "manager@utdallas.edu",
                                "timestamp" : "2019-03-01T15:00:00Z",
                                "comment" : "approved",
                                "oldState" : "pending",
                                "newState" : "approved"
                            }
                        ]
                    }
                  ]

    $scope.toggleCollapse = function(e) {
        var target = e.currentTarget;
        $(target.nextElementSibling).toggle();
    };

    $scope.getMaxBudgetStr = function() {
        return "$" + $scope.maxBudget;
    };

    $scope.getTotal = function() {
        var total = 0
        for (var i = 0; i < $scope.data.length; i++) {
            if ($scope.data[i].status == "approved") {
                total += $scope.data[i].cost;
            }
        }
        return $scope.maxBudget - total;
    };

    $scope.getTotalStr = function() {
        return "$" + $scope.getTotal();
    };

    $scope.getPending = function() {
        var total = 0
        for (var i = 0; i < $scope.data.length; i++) {
            if ($scope.data[i].status == "approved" || $scope.data[i].status == "pending") {
                total += $scope.data[i].cost;
            }
        }
        return $scope.maxBudget - total;
    };

    $scope.getPendingStr = function() {
        return "$" + $scope.getPending();
    };

    console.log($scope);
    * */

    $scope.procurementData = []
    $http.post('/procurementStatuses', {}).then(function(resp) {
        console.log("Status Success", resp)
        $scope.procurementData = resp.data;
    }, function(err) {
        console.error("Status Error", err.data)
    });

    $scope.costData = []
    $http.post('/getCosts', {}).then(function(resp) {
        console.log("Costs Success", resp)
        $scope.costData = resp.data;
    }, function(err) {
        console.error("Costs Error", err.data)
    });

    $scope.projectData = []
    $http.post('/findProject', {}).then(function(resp) {
        console.log("Project Success", resp)
        $scope.projectData = resp.data;
    }, function(err) {
        console.error("Project Error", err.data)
    });

    $scope.getMaxBudgetStr = function() {
        console.log($scope.projectData);
        if ($scope.projectData.length != 0) {
            return "$" + $scope.projectData[0]["defaultBudget"];
        }
        return "$0";
    };

    $scope.getTotalStr = function() {
        if ($scope.projectData.length != 0) {
            return "$" + $scope.projectData[0]["availableBudget"];
        }
        return "$0";
    };

    $scope.getPendingStr = function() {
        if ($scope.projectData.length != 0) {
            return "$" + $scope.projectData[0]["pendingBudget"];
        }
        return "$0";
    };
}]);
