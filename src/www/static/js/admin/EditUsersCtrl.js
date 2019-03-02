app.controller('EditUsersCtrl', ['$scope', '$location', function($scope, $location) {

    $scope.fieldKeys = ["groupID", "firstName", "lastName", "netID", "email", "course"];
    $scope.fields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course"];

    $scope.users = [ {
                        "groupID": "123",
                        "firstName": "Mack",
                        "lastName": "Packett",
                        "netID": "mpp123456",
                        "email": "packet@utdallas.edu",
                        "course": "CS 4485"
                    },
                    {
                        "groupID": "456",
                        "firstName": "Bob",
                        "lastName": "Builder",
                        "netID": "bbb111111",
                        "email": "bob@utdallas.edu",
                        "course": "CS 4485"
                    },
                    {
                        "groupID": "222",
                        "firstName": "Monika",
                        "lastName": "Mulder",
                        "netID": "mmm987654",
                        "email": "monika@utdallas.edu",
                        "course": "CS 4485"
                    }
                  ]

    $scope.editUser = function(e) {
        var target = e.currentTarget;
        console.log(target);
        document.getElementById("editModal").style.display = "block";
    };

    $scope.closeEditBox = function(e) {
        document.getElementById("editModal").style.display = "none";
    };

}]);