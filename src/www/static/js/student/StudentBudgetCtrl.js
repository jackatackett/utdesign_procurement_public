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

    function convertCosts(value) {
        value = String(value);
        return value.slice(0, -2) + "." + value.slice(value.length-2);
    }

    var numProjects = -1;   //TODO: what happens if this is 0 or -1?
    
    //~ var currentProj = projectData[0]["projectNumber"]    //used to select which tab is shown
    var currentProj = 0   //used to select which tab is shown

    $scope.requestKeys = ["status", "vendor", "requestTotal"];
    $scope.requestFields = ["Status", "Vendor", "Cost"];

    $scope.costKeys = ["type", "comment", "amount"];
    $scope.costFields = ["Type", "Comment", "Amount"];

    $scope.curRequestData = [];
    $scope.curCostData = [];
    
    var procurementData = [];
    
    var costData = [];
    
    $scope.projects = []

    var projectData = [];
    $http.post('/findProject', {}).then(function(resp) {
        console.log("Project Success", resp);
        projectData = resp.data;

        numProjects = projectData.length;
        console.log("number projects: " + numProjects);

        for (var pr in projectData) {
            var tempData = {}
            tempData["number"] = projectData[pr]["projectNumber"];
            tempData["name"] = projectData[pr]["projectName"];
            $scope.projects.push(tempData);
            //~ $scope.projects.push({"number": pr["projectNumber"], "name": pr["projectName"]});
        }
        console.log("project mapping:");
        console.log($scope.projects);
    }, function(err) {
        console.error("Project Error", err.data)
    }).then(function(resp) {
        $http.post('/procurementStatuses', {}).then(function(resp) {
            console.log("Status Success", resp);
            procurementData = resp.data;
            filterRequests();
            console.log("current requests:");
            console.log($scope.curRequestData);
        }, function(err) {
            console.error("Status Error", err.data);
        });
    }).then(function(resp) {
        $http.post('/getCosts', {}).then(function(resp) {
            console.log("Costs Success", resp);
            costData = resp.data;
            filterCosts();
        }, function(err) {
            console.error("Costs Error", err.data);
        });
    });

    function filterRequests() {
        $scope.curRequestData = [];
        for (var req in procurementData) {
            procurementData[req]["requestTotal"] = "-$" + convertCosts(procurementData[req]["requestTotal"]);
            if (procurementData[req]["projectNumber"] == $scope.projects[currentProj]["number"]) {
                $scope.curRequestData.push(procurementData[req]);
            }
        }
    }

    function filterCosts() {
        $scope.curCostData = [];
        for (var co in costData) {
            if (costData[co]["type"] == "refund") {
                costData[co]["amount"] = "+$" + convertCosts(costData[co]["amount"]);
            }
            else {
                costData[co]["amount"] = "-$" + convertCosts(costData[co]["amount"]);
            }
            if (costData[co]["projectNumber"] == $scope.projects[currentProj]["number"]) {
                $scope.curCostData.push(costData[co]);
            }
        }
    }
    
    $scope.getMaxBudgetStr = function() {
        //~ console.log(projectData);
        if (numProjects > 0) {
            return "$" + convertCosts(projectData[currentProj]["defaultBudget"]);
        }
        return "$0";
    };

    $scope.getTotalStr = function() {
        if (numProjects > 0) {
            return "$" + convertCosts(projectData[currentProj]["availableBudget"]);
        }
        return "$0";
    };

    $scope.getPendingStr = function() {
        if (numProjects > 0) {
            return "$" + convertCosts(projectData[currentProj]["pendingBudget"]);
        }
        return "$0";
    };

    $scope.regenerateTable = function(e) {
        var targ = e.target.id.substring(6, e.target.id.length);
        currentProj = targ;
        filterRequests();
        filterCosts();
        
        /*if (targ == "All") {        //taken from old manager code; "All" should only be for manager
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
        }*/
    };
}]);
