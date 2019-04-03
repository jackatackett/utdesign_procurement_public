app.controller('ViewRequestsCtrl', ['$scope', '$location', '$http', '$window', '$timeout', '$interval', function($scope, $location, $http, $window, $timeout, $interval) {
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

    $scope.fieldKeys = ["projectNumber", "status", "vendor", "URL", "justification", "additionalInfo"];
    $scope.fields = ["Project Number", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "totalCost"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.teams = ["Procurement", "Clock-It", "Smart Glasses"];

    $scope.mgrComment = "";

    $scope.projects = [];

    var projectData = [];
    var curProject = 0;

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

    $scope.lightboxRow = 0;

    $scope.toggleCollapse = function(e) {
        var target = e.currentTarget;
        $(target.nextElementSibling).toggle();
    };

    $scope.regenerateTable = function(e) {
        //~ var target = e.currentTarget;
        //~ console.log("change table");
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
        console.log("status number", curProject);
        var filterData = {"projectNumbers": $scope.projects[curProject]["number"]};
        console.log("Filtering:", filterData);
        $http.post('/procurementStatuses', filterData).then(function(resp) {
            console.log("Success", resp)
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
