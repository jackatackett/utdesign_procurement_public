app.controller('ManagerBudgetCtrl', ['$scope', function($scope, $http) {
    console.log("budget");

    $scope.fieldKeys = ["projectID", "status", "vendor", "URL", "justification", "additionalInfo", "cost"];
    $scope.fields = ["Project ID", "Status", "Vendor", "URL", "Justification", "Additional Info", "Cost"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];

    $scope.teams = {
                        "Procurement": 123,
                        "Clock-It": 124,
                        "Smart Glasses": 125
                    };  //will need to extract this
    $scope.teams["All"] = "All";

    $scope.maxBudget = 2000.00;             //need to pull this from a defaults list

    $scope.allData = [ {
                        projectID: 123,
                        status: "pending",
                        vendor: "Home Depot",
                        URL: "homedepot.com",
                        justification: "Because he told me toooooo",
                        additionalInfo: "He is Plankton",
                        items: [ {
                                description: "A big thing",
                                partNo: "9001",
                                quantity: 25,
                                unitCost: 1000000000,
                                total: 25000000000                  //where is this from?
                            },
                            {
                                description: "A small thing",
                                partNo: "9002",
                                quantity: 250,
                                unitCost: 10,
                                total: 2500                         //where is this from?
                            }
                        ],
                        cost: 5     //is this stored in the database? if not, need to calculate it: needs to include shipping/taxes/etc if needed
                    },
                    {
                        projectID: 124,
                        status: "approved",
                        vendor: "The Plastic Store",
                        URL: "gmail.com",
                        justification: "O Captain, My Captain",
                        additionalInfo: "He is dead, Jim",
                        items: [ {
                                description: "A hunk of plastic",
                                partNo: "9003",
                                quantity: 1,
                                unitCost: 10,
                                total: 10
                            }
                        ],
                        cost: 10
                    }
                  ];
    $scope.data = $scope.allData;

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

    $scope.regenerateTable = function(e) {
        var targ = e.target.id.substring(6, e.target.id.length);
        if (targ == "All") {
            $scope.data = $scope.allData;
            $("#currentGroupBudget").hide();
        }
        else {
            $("#currentGroupBudget").show();
            $scope.data = [];
            for (var i = 0; i < $scope.allData.length; i++) {
                if ($scope.allData[i]["projectID"] == $scope.teams[targ]) {
                    $scope.data.push($scope.allData[i]);
                }
            }
        }
    };
}]);
