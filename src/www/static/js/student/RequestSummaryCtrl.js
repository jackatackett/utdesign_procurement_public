app.controller('RequestSummaryCtrl', ['$scope', '$http', '$location', '$timeout', 'dispatcher', function($scope, $http, $location, $timeout, dispatcher) {

    $scope.fieldKeys = ["requestNumber", "projectNumber", "manager", "status", "vendor", "URL", "justification", "additionalInfo"];
    $scope.fields = ["Request Number", "Project Number", "Assigned Manager Email", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "itemURL", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Item URL", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];

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

    $scope.toggleCollapse = function(e) {
        var target = e.currentTarget;
        $(target.nextElementSibling).toggle();
    };

    $scope.editRequest = function(request) {
        dispatcher.emit('editRequest', request);
        $location.hash('create');
    }

    $scope.cloneRequest = function(request) {
        dispatcher.emit('cloneRequest', request);
        $location.hash('create');
    }

    $scope.cancelRequest = function(request) {
        if (request._id) {
            $http.post('/procurementCancel', {_id: request._id}).then(function(resp) {
                console.log(resp);
                alert("Success!");
                $scope.refreshStatuses();
            }, function(err) {
                console.error(err);
                alert("Error!");
                $scope.refreshStatuses();
            })
        } else {
            console.error("Cancel Request cannot proceed without _id. See:", request);
            alert("Cancel Request cannot proceed without _id.");
        }
    }

    $scope.canEdit = function(status) {
        return status == "saved" || status == "updates for manager" || status == "updates for admin";
    }

    $scope.refreshStatuses = function() {
        $http.post('/procurementStatuses', {}).then(function(resp) {
            console.log("procurementStatuses success", resp)
            $scope.data = resp.data;
        }, function(err) {
            console.error("Error", err.data)
        });
    }

    $timeout(0, $scope.refreshStatuses())

    dispatcher.on("refreshStatuses", $scope.refreshStatuses);

}]);