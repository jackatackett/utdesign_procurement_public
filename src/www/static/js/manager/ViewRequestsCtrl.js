app.controller('ViewRequestsCtrl', ['$scope', '$location', '$http', '$window', '$timeout', '$interval', 'statusLut', function($scope, $location, $http, $window, $timeout, $interval, statusLut) {

    $scope.statusLut = statusLut;

    function convertCosts(value) {
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
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Item Cost"];
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
        $scope.refreshStatuses();
    };

    $scope.approveRequest = function(e, rowIdx) {
        $http.post('/procurementApproveManager', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
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
        // determine which projects the manager is assigned to
        $http.post('/findProject', {}).then(function(resp) {
            projectData = resp.data;
            numProjects = projectData.length;
            $scope.projects = [];

            for (var pr in projectData) {
                var tempData = {}
                tempData["number"] = projectData[pr]["projectNumber"];
                tempData["name"] = projectData[pr]["projectName"];
                $scope.projects.push(tempData);
            }

            // refresh table as soon as project membership of manager is known
            $scope.refreshStatuses();
        }, function(err) {
            console.error("Error", err.data);
        });
    };

    $scope.refreshStatuses = function() {
        // may only show requests of one project at a time,
        // by default the "first" project in the list returned by getTeams() is shown
        var filterData = {"projectNumbers": $scope.projects[curProject]["number"]};
        $http.post('/procurementStatuses', filterData).then(function(resp) {
            $scope.data = cleanData(resp.data);
        }, function(err) {
            console.error("Error", err.data)
        });
    };

    // table cannot refresh until manager's project membership is known
    $scope.getTeams();
    $timeout($scope.refreshStatuses, 0);
    // table of procurement requests refreshes every 5 seconds
    $interval($scope.refreshStatuses, 5000);

    $scope.historyFields = ["Timestamp", "Source", "Comment", "Old State", "New State"];
    $scope.historyFieldKeys = ["timestamp", "actor", "comment", "oldState", "newState"];

    $scope.viewHistory = function(e, rowIdx) {
        $("#historyBody").empty();
        var historyHTML = "";
        for (var hist in $scope.data[rowIdx]["history"]) {
            historyHTML += '<tr style="border-bottom: 1.5px solid black">';
            for (var ele in $scope.historyFieldKeys) {
                if ($scope.historyFieldKeys[ele] == "oldState" || $scope.historyFieldKeys[ele] == "newState") {
                    historyHTML += '<td scope="col" style="background-color: #eee;">' + statusLut[$scope.data[rowIdx]["history"][hist][$scope.historyFieldKeys[ele]]] + '</td>';
                }
                else {
                    historyHTML += '<td scope="col" style="background-color: #eee;">' + $scope.data[rowIdx]["history"][hist][$scope.historyFieldKeys[ele]] + '</td>';
                }
            }
            historyHTML += '</tr>';
        }
        if (historyHTML == "") {
            historyHTML = "No history";
        }
        $("#historyBody").append(historyHTML);
        $("#historyModal").show();
    };

    $scope.closeHistoryBox = function(e) {
        $("#historyModal").hide();
    };
}]);
