app.controller('ViewRequestsCtrl', ['$scope', '$location', '$http', '$window', '$timeout', function($scope, $location, $http, $window, $timeout) {

$scope.fieldKeys = ["projectNumber", "status", "vendor", "URL", "justification", "additionalInfo"];
    $scope.fields = ["Project Number", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.teams = ["Procurement", "Clock-It", "Smart Glasses"];

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
        var target = e.currentTarget;
        console.log("change table");
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
        $("#rejectModal").show();
        lightboxRow = rowIdx;
    };

    $scope.permanentReject = function(e) {
        $http.post('/procurementRejectManager', {'_id':$scope.data[lightboxRow]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $window.location.reload();
        }, function(err) {
            console.error("Error", err.data)
            alert("Error")
        });
    };

    $scope.sendForReview = function(e) {
        $http.post('/procurementUpdateManager', {'_id':$scope.data[lightboxRow]._id}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $window.location.reload();
        }, function(err) {
            console.error("Error", err.data)
            alert("Error")
        });
    };

    $scope.closeRejectBox = function(e) {
        $("#rejectModal").hide();
    };

    $scope.refreshStatuses = function() {
        $http.post('/procurementStatuses', {}).then(function(resp) {
            console.log("Success", resp)
            $scope.data = resp.data;
        }, function(err) {
            console.error("Error", err.data)
        });
    }

    $timeout($scope.refreshStatuses, 0);

}]);
