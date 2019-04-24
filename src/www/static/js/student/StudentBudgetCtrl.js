app.controller('StudentBudgetCtrl', ['$scope', '$location', '$http', '$window', '$timeout', '$interval', 'statusLut', 'costTypeLut', function($scope, $location, $http, $window, $timeout, $interval, statusLut, costTypeLut) {

    $scope.statusLut = statusLut;
    $scope.costTypeLut = costTypeLut;

    function convertCosts(value) {
        if (typeof value === "undefined") {
            return "0.00";
        }
        value = String(value);
        if (value !== "undefined") {
            while (value.length < 3) {
                value = "0" + value;
            }
            return value.slice(0, -2) + "." + value.slice(value.length-2);
        }
        return "0.00"
    };

    var numProjects = -1;   //TODO: what happens if this is 0 or -1?
    
    //~ var currentProj = projectData[0]["projectNumber"]    //used to select which tab is shown
    var currentProj = 0   //used to select which tab is shown

    $scope.requestKeys = ["status", "vendor", "requestSubtotal", "shippingCost", "requestTotal"];
    $scope.requestFields = ["Status", "Vendor", "Subtotal", "Shipping", "Total"];

    $scope.costKeys = ["timestamp", "type", "comment", "amount"];
    $scope.costFields = ["Timestamp", "Type", "Comment", "Amount"];

    $scope.curRequestData = [];
    $scope.curCostData = [];
    
    var procurementData = [];
    
    var costData = [];
    
    $scope.projects = [];
    var curProject = 0;
    var projectData = [];

    $scope.getTeams = function() {
        $http.post('/findProject', {}).then(function(resp) {
            projectData = resp.data;

            numProjects = projectData.length;

            $scope.projects = [];

            for (var pr in projectData) {
                var tempData = {}
                tempData["number"] = projectData[pr]["projectNumber"];
                tempData["name"] = projectData[pr]["projectName"];
                $scope.projects.push(tempData);
                //~ $scope.projects.push({"number": pr["projectNumber"], "name": pr["projectName"]});
            }
        }, function(err) {
            console.error("Error", err.data);
        });
    };

    $scope.getData = function() {
        var filterData = {"projectNumbers": [$scope.projects[currentProj]["number"]]};
        $http.post('/procurementStatuses', filterData).then(function(resp) {
            procurementData = resp.data;
            filterRequests();
        }, function(err) {
            console.error("Status Error", err.data);
        });
        $http.post('/getCosts', filterData).then(function(resp) {
            costData = resp.data;
            filterCosts();
        }, function(err) {
            console.error("Costs Error", err.data);
        });
    };

    //~ $scope.getTeams();
    $timeout($scope.getTeams, 0);
    $interval($scope.getTeams, 5000);
    $timeout($scope.getData, 500);
    $interval($scope.getData, 5000);

    function filterRequests() {
        $scope.curRequestData = [];
        for (var req in procurementData) {
            procurementData[req]["requestSubtotal"] = "$" + convertCosts(procurementData[req]["requestSubtotal"]);
            procurementData[req]["shippingCost"] = "$" + convertCosts(procurementData[req]["shippingCost"]);
            procurementData[req]["requestTotal"] = "+$" + convertCosts(procurementData[req]["requestTotal"]);
            //~ if (procurementData[req]["projectNumber"] == $scope.projects[currentProj]["number"]) {
                //~ $scope.curRequestData.push(procurementData[req]);
            //~ }
        }
        $scope.curRequestData = procurementData;
    };

    function filterCosts() {
        $scope.curCostData = [];
        for (var co in costData) {
            if (costData[co]["type"] == "refund") {
                costData[co]["amount"] = "-$" + convertCosts(costData[co]["amount"]);
            }
            else if (costData[co]["type"] == "reimbursement") {
                costData[co]["amount"] = "+$" + convertCosts(costData[co]["amount"]);
            }
            else {
                costData[co]["amount"] = "$" + convertCosts(costData[co]["amount"]);
            }
            //~ if (costData[co]["projectNumber"] == $scope.projects[currentProj]["number"]) {
                //~ $scope.curCostData.push(costData[co]);
            //~ }
        }
        $scope.curCostData = costData;
    };
    
    $scope.getMaxBudgetStr = function() {
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
        $scope.getData();
        //~ filterRequests();
        //~ filterCosts();
        
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
