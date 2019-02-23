app.controller('AddUsersCtrl', ['$scope', '$location', function($scope, $location) {

    $scope.fieldKeys = ["groupID", "status", "vendor", "URL", "justification", "additionalInfo"];
    $scope.fields = ["Group ID", "Status", "Vendor", "URL", "Justification", "Additional Info"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.teams = ["Procurement", "Clock-It", "Smart Glasses"];
    $scope.filters = ["Pending", "Accepted", "Rejected", "Shipped", "Canceled", "Completed"];
    $scope.userData = ["First Name", "Last Name", "NetID", "Email", "GroupID", "Course Name"];

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

    $scope.addUser = function(e) {
        var target = e.currentTarget;
        console.log("adding one user");
    };

     $scope.uploadSpreadsheet = function(e) {
        var target = e.currentTarget;
        console.log("upload spreadsheet of multiple users");
    };

}]);
