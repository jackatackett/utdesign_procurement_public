app.controller('EditUsersCtrl', ['$scope', '$location', function($scope, $location) {

    $scope.fieldKeys = ["projectNumber", "firstName", "lastName", "netID", "email", "course"];
    $scope.fields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course"];

    $scope.users = [ {
                        "projectNumber": 123,
                        "firstName": "Mack",
                        "lastName": "Packett",
                        "netID": "mpp123456",
                        "email": "packet@utdallas.edu",
                        "course": "CS 4485"
                    },
                    {
                        "projectNumber": 456,
                        "firstName": "Bob",
                        "lastName": "Builder",
                        "netID": "bbb111111",
                        "email": "bob@utdallas.edu",
                        "course": "CS 4485"
                    },
                    {
                        "projectNumber": 222,
                        "firstName": "Monika",
                        "lastName": "Mulder",
                        "netID": "mmm987654",
                        "email": "monika@utdallas.edu",
                        "course": "CS 4485"
                    }
                  ]

    $scope.selectedUser = {};

    $scope.editUser = function(e, rowIdx) {
        $("#editModal").show();
        $scope.selectedUser = {};
        var user = $scope.users[rowIdx];
        for (var key in user) {
            if (user.hasOwnProperty(key)) {
                $scope.selectedUser[key] = user[key];
            }
        }
    };

    $scope.closeEditBox = function(e) {
        //~ document.getElementById("editModal").style.display = "none";
        $("#editModal").hide();
    };

    $scope.saveUserEdit = function() {
        //need to validate input
        console.log($scope.selectedUser);
        $("#editModal").hide();
    }

}]);
