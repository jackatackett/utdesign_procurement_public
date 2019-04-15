app.controller('AddUsersCtrl', ['$scope', 'dispatcher', '$location', '$http', '$window', function($scope, dispatcher, $location, $http, $window) {

    $scope.errorText = "";
    $scope.fieldKeys = ["projectNumbers", "firstName", "lastName", "netID", "email", "course"];
    $scope.fields = ["Project Number(s)", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.bulkKeys = ["projectNumbers", "firstName", "lastName", "netID", "email", "course", "role", "comment"];
    $scope.bulkFields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course", "Role", "Comment"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number(s)", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.userInfo = {};
    $scope.projectNumArray = [];
    $scope.numberOfPages = 1;
    $scope.currentPage = 1;
    $scope.pageNumberArray = [];

    $scope.users = []

    $scope.addUser = function(e) {
        var target = e.currentTarget;

        if($scope.userInfo.projectNumbers) {
            var prjNumsAry = $scope.userInfo.projectNumbers.replace(' ', '').split(',');
            for(var n in prjNumsAry) {
                prjNumsAry[n] = Number(prjNumsAry[n]);
            }
            $scope.projectNumArray = prjNumsAry;
        }

        if(!validateRequest()) {
            console.log("request was invalid");
        } else {
            $http.post('/userAdd', {'projectNumbers':prjNumsAry, 'firstName':$scope.userInfo.firstName, 'lastName':$scope.userInfo.lastName, 'netID':$scope.userInfo.netID, 'email':$scope.userInfo.email, 'course':$scope.userInfo.course, 'role':'student'}).then(function(resp) {
                console.log("Success", resp);
            }, function(err) {
                console.error("Error", err.data);
                alert("Error")
            });
        }
    };

    $scope.selectSpreadsheet = function(e) {
        console.log("selectSpreadsheet");
        var target = e.currentTarget;
        $("#spreadsheetField").click();
    };

    $scope.submitSpreadsheet = function(files) {
        console.log("submitSpreadsheet");

        var fd = new FormData();
        //Take the first selected file
        fd.append("sheet", files[0]);

        $http.post('/userSpreadsheetUpload', fd, {
            withCredentials: true,
            headers: {'Content-Type': undefined },
            transformRequest: angular.identity
        }).then(function(resp) {
            $scope.bulkData = resp.data;
            $scope.showBulk();
            dispatcher.emit('bulkRefresh')
        }, function(err) {
            alert("Error!", err);
        });
    }

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

    $scope.showBulk = function() {
        $location.hash("addUserBulk");
    };

    function validateRequest() {
        var valid = false;

        $http.post('/projectValidate', {'projectNumbers': $scope.projectNumArray}).then(function(resp) {
            if(resp.data === "true") {
                valid = true;
            }
            if (valid === false) {
                $scope.errorText = "Invalid Project Number";
                return false;
            }
        }, function(err) {
            console.error("project validate fail", err)
        });

        if(!$scope.userInfo.firstName || $scope.userInfo.firstName.length <= 0) {
            $scope.errorText = "First name must not be empty";
            return false;
        }

        if(!$scope.userInfo.lastName || $scope.userInfo.lastName.length <= 0) {
            $scope.errorText = "Last name must not be empty";
            return false;
        }

        if(!$scope.userInfo.email || $scope.userInfo.email.length <= 0) {
            $scope.errorText = "Email must not be empty";
            return false;
        }

        if(!$scope.userInfo.course || $scope.userInfo.course.length <= 0) {
            $scope.errorText = "Course must not be empty";
            return false;
        }

        $scope.errorText = "";
        return true;
    }

}]);
