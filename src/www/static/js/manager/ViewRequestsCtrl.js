app.controller('ViewRequestsCtrl', ['$scope', '$location', '$http', '$window', '$timeout', '$interval', 'statusLut', function($scope, $location, $http, $window, $timeout, $interval, statusLut) {

    $scope.statusLut = statusLut;

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
            result[d]["requestTotal"] = convertCosts(data[d]["requestTotal"]);
            result[d]["shippingCost"] = convertCosts(data[d]["shippingCost"]);
        }
        return result;
    };

    $scope.fieldKeys = ["requestNumber", "projectNumber", "status", "vendor", "URL", "requestTotal", "shippingCost"];
    $scope.fields = ["Request Number", "Project Number", "Status", "Vendor", "URL", "Total Cost", "Shipping Cost"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "totalCost"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.teams = ["Procurement", "Clock-It", "Smart Glasses"];

    $scope.mgrComment = "";

    $scope.projects = [];

    var projectData = [];
    var curProject = 0;

    $scope.data = []

    $scope.lightboxRow = 0;

    $scope.toggleCollapse = function(e) {
        var target = e.currentTarget;
        $(target.nextElementSibling).toggle();
    };

    $scope.regenerateTable = function(e) {
        var targ = e.target.id.substring(6, e.target.id.length);
        curProject = targ;
        console.log("current proj: ", curProject);
        console.log("project data:", projectData[curProject]);
        console.log("project info:", $scope.projects);
        $scope.refreshStatuses();
    };

    $scope.approveRequest = function(e, rowIdx) {
        console.log($scope.data);
        console.log(rowIdx);
        $http.post('/procurementApproveManager', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $window.location.reload();
        }, function(err) {
            console.error("Error", err.data)
            alert("Error")
        });
    };

    $scope.rejectRequest = function(e, rowIdx) {
        $scope.mgrComment = "";
        $("#rejectModal").show();
        lightboxRow = rowIdx;
    };

    $scope.permanentReject = function(e) {
        $http.post('/procurementRejectManager', {'_id':$scope.data[lightboxRow]._id, "comment": $scope.mgrComment}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $window.location.reload();
        }, function(err) {
            console.error("Error", err.data)
            alert("Error")
            $scope.mgrComment = "";
        });
    };

    $scope.sendForReview = function(e) {
        $http.post('/procurementUpdateManager', {'_id':$scope.data[lightboxRow]._id, "comment": $scope.mgrComment}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $window.location.reload();
        }, function(err) {
            console.error("Error", err.data)
            alert("Error")
            $scope.mgrComment = "";
        });
    };

    $scope.canApprove = function(status) {
        return status == 'pending';
    };

    $scope.closeRejectBox = function(e) {
        $scope.mgrComment = "";
        $("#rejectModal").hide();
    };

    $scope.getTeams = function() {
        $http.post('/findProject', {}).then(function(resp) {
            console.log("Project Success", resp);
            projectData = resp.data;

            numProjects = projectData.length;
            console.log("number projects: " + numProjects);

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

    $scope.refreshStatuses = function() {
        var filterData = {"projectNumbers": $scope.projects[curProject]["number"]};
        $http.post('/procurementStatuses', filterData).then(function(resp) {
            $scope.data = cleanData(resp.data);
        }, function(err) {
            console.error("Error", err.data)
        });
    };

    $scope.getTeams();
    $timeout($scope.refreshStatuses, 0);
    $interval($scope.refreshStatuses, 5000);

    $scope.historyFields = ["Timestamp", "Source", "Comment", "Old State", "New State"];
    $scope.historyFieldKeys = ["timestamp", "actor", "comment", "oldState", "newState"];

    $scope.viewHistory = function(e, rowIdx) {
        console.log("history");
        $("#historyBody").empty();
        var historyHTML = "";
        for (var hist in $scope.data[rowIdx]["history"]) {
            historyHTML += '<tr style="border-bottom: 1.5px solid black">';
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
