app.controller('ViewRequestsCtrl', ['$scope', '$location', '$http', function($scope, $location, $http) {

$scope.fieldKeys = ["groupID", "status", "vendor", "URL", "justification", "additionalInfo"];
    $scope.fields = ["Group ID", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.teams = ["Procurement", "Clock-It", "Smart Glasses"];

    $scope.data = [ {
                        groupID: "123",
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
                        groupID: "124",
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

    $scope.currentRow = 0;

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
        $http.post('/procurementApprove', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
            console.log("Success", resp)
        }, function(err) {
            console.error("Error", err.data)
        });
    };

    $scope.rejectRequest = function(e, rowIdx) {
        $("#rejectModal").show();
        currentRow = rowIdx;
    };

    $scope.permanentReject = function(e, rowIdx) {
        $http.post('/procurementReject', {'_id':$scope.data[currentRow]._id}).then(function(resp) {
            console.log("Success", resp)
        }, function(err) {
            console.error("Error", err.data)
        });
    };

    $scope.sendForReview = function(e) {
        $http.post('/procurementReview', {'_id':$scope.data[currentRow]._id}).then(function(resp) {
            console.log("Success", resp)
        }, function(err) {
            console.error("Error", err.data)
        });
    };

    $scope.closeRejectBox = function(e) {
        $("#rejectModal").hide();
    };

    $http.post('/procurementStatuses', {}).then(function(resp) {
        console.log("Success", resp)
        $scope.data = resp.data;
    }, function(err) {
        console.error("Error", err.data)
    });

}]);
