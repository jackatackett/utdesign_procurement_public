app.controller('ManagerBudgetCtrl', ['$scope', '$location', '$http', '$window', function($scope, $location, $http, $window) {
    console.log("budget");

    //~ $scope.fieldKeys = ["projectID", "status", "vendor", "URL", "justification", "additionalInfo", "cost"];
    //~ $scope.fields = ["Project ID", "Status", "Vendor", "URL", "Justification", "Additional Info", "Cost"];
    //~ $scope.grid = [];
    //~ $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    //~ $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];

    //~ $scope.teams = {
                        //~ "Procurement": 123,
                        //~ "Clock-It": 124,
                        //~ "Smart Glasses": 125
                    //~ };  //will need to extract this
    //~ $scope.teams["All"] = "All";

    //~ $scope.maxBudget = 2000.00;             //need to pull this from a defaults list

    //~ $scope.allData = [ {
                        //~ projectID: 123,
                        //~ status: "pending",
                        //~ vendor: "Home Depot",
                        //~ URL: "homedepot.com",
                        //~ justification: "Because he told me toooooo",
                        //~ additionalInfo: "He is Plankton",
                        //~ items: [ {
                                //~ description: "A big thing",
                                //~ partNo: "9001",
                                //~ quantity: 25,
                                //~ unitCost: 1000000000,
                                //~ total: 25000000000                  //where is this from?
                            //~ },
                            //~ {
                                //~ description: "A small thing",
                                //~ partNo: "9002",
                                //~ quantity: 250,
                                //~ unitCost: 10,
                                //~ total: 2500                         //where is this from?
                            //~ }
                        //~ ],
                        //~ cost: 5     //is this stored in the database? if not, need to calculate it: needs to include shipping/taxes/etc if needed
                    //~ },
                    //~ {
                        //~ projectID: 124,
                        //~ status: "approved",
                        //~ vendor: "The Plastic Store",
                        //~ URL: "gmail.com",
                        //~ justification: "O Captain, My Captain",
                        //~ additionalInfo: "He is dead, Jim",
                        //~ items: [ {
                                //~ description: "A hunk of plastic",
                                //~ partNo: "9003",
                                //~ quantity: 1,
                                //~ unitCost: 10,
                                //~ total: 10
                            //~ }
                        //~ ],
                        //~ cost: 10
                    //~ }
                  //~ ];
    //~ $scope.data = $scope.allData;

    //~ $scope.toggleCollapse = function(e) {
        //~ var target = e.currentTarget;
        //~ $(target.nextElementSibling).toggle();
    //~ };

    //~ $scope.getMaxBudgetStr = function() {
        //~ return "$" + $scope.maxBudget;
    //~ };

    //~ $scope.getTotal = function() {
        //~ var total = 0
        //~ for (var i = 0; i < $scope.data.length; i++) {
            //~ if ($scope.data[i].status == "approved") {
                //~ total += $scope.data[i].cost;
            //~ }
        //~ }
        //~ return $scope.maxBudget - total;
    //~ };

    //~ $scope.getTotalStr = function() {
        //~ return "$" + $scope.getTotal();
    //~ };

    //~ $scope.getPending = function() {
        //~ var total = 0
        //~ for (var i = 0; i < $scope.data.length; i++) {
            //~ if ($scope.data[i].status == "approved" || $scope.data[i].status == "pending") {
                //~ total += $scope.data[i].cost;
            //~ }
        //~ }
        //~ return $scope.maxBudget - total;
    //~ };

    //~ $scope.getPendingStr = function() {
        //~ return "$" + $scope.getPending();
    //~ };

    //~ $scope.regenerateTable = function(e) {
        //~ var targ = e.target.id.substring(6, e.target.id.length);
        //~ if (targ == "All") {
            //~ $scope.data = $scope.allData;
            //~ $("#currentGroupBudget").hide();
        //~ }
        //~ else {
            //~ $("#currentGroupBudget").show();
            //~ $scope.data = [];
            //~ for (var i = 0; i < $scope.allData.length; i++) {
                //~ if ($scope.allData[i]["projectID"] == $scope.teams[targ]) {
                    //~ $scope.data.push($scope.allData[i]);
                //~ }
            //~ }
        //~ }
    //~ };

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
