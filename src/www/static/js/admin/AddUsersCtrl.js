app.controller('AddUsersCtrl', ['$scope', '$location', '$http', '$window', function($scope, $location, $http, $window) {

    $scope.fieldKeys = ["projectNumber", "firstName", "lastName", "netID", "email", "course"];
    $scope.fields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.userInfo = {};

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

    $scope.addUser = function(e) {
        var target = e.currentTarget;

        $http.post('/userAdd', {'projectNumbers':Number($scope.userInfo.projectNumber), 'firstName':$scope.userInfo.firstName, 'lastName':$scope.userInfo.lastName, 'netID':$scope.userInfo.netID, 'email':$scope.userInfo.email, 'course':$scope.userInfo.course, 'role':'student'}).then(function(resp) {
            console.log("Success", resp);
            alert("Success!");
            $window.location.reload();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error")
        });
    };

    $scope.uploadSpreadsheet = function(e) {
        var target = e.currentTarget;
        console.log("upload spreadsheet");
        $("#spreadsheetField").click();
    };

    $scope.regeneratePage = function(e) {
        var target = e.currentTarget;
        var id = target.id;

        if (id == "addUserButton") {
            document.getElementById("addUserTable").style.display = "table";
            document.getElementById("editUserTable").style.display = "none";
            document.getElementById("editSearchBox").style.display = "none";
        } else {
            document.getElementById("editUserTable").style.display = "table";
            document.getElementById("editSearchBox").style.display = "block";
            document.getElementById("addUserTable").style.display = "none";
        }
    };

}]);
