app.controller('AddProjectsCtrl', ['$scope', '$location', '$http', '$window', function($scope, $location, $http, $window) {

    $scope.errorText = "";
    $scope.fieldKeys = ["projectNumber", "sponsorName", "projectName", "membersEmails", "defaultBudget"];
    $scope.fields = ["Project Number", "Sponsor Name", "Project Name", "Members Emails", "Budget"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number(s)", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.projectInfo = {};
    $scope.projectNumArray = [];

    $scope.users = []

    $scope.addProject = function(e) {
        var target = e.currentTarget;

        if(!validateRequest()) {
            console.log("request was invalid");
        } else {
            $http.post('/projectAdd', {'projectNumber':Number($scope.projectInfo.projectNumber), 'sponsorName':$scope.projectInfo.sponsorName, 'projectName':$scope.projectInfo.projectName, 'membersEmails':$scope.projectInfo.members, 'defaultBudget':Number($scope.projectInfo.defaultBudget), 'availableBudget':Number($scope.projectInfo.defaultBudget), 'pendingBudget':Number($scope.projectInfo.defaultBudget)}).then(function(resp) {
                console.log("Success", resp);
            }, function(err) {
                console.error("Error", err.data);
                alert("Error")
            });
        }
    };

    $scope.selectSpreadsheet = function(e) {
          console.log("selectSpreadsheet");
//        var target = e.currentTarget;
//        $("#spreadsheetField").click();
    };

    $scope.submitSpreadsheet = function(files) {
          console.log("submitSpreadsheet");
//
//        var fd = new FormData();
//        //Take the first selected file
//        fd.append("sheet", files[0]);
//
//        $http.post('/userAddBulk', fd, {
//            withCredentials: true,
//            headers: {'Content-Type': undefined },
//            transformRequest: angular.identity
//        }).then(function(resp) {
//            console.log("userAddBulk success", resp)
//        }, function(err) {
//            console.error("userAddBulk fail", err)
//        });
    }

    $scope.regeneratePage = function(e) {
//        var target = e.currentTarget;
//        var id = target.id;
//
//        if (id == "addUserButton") {
//            document.getElementById("addUserTable").style.display = "table";
//            document.getElementById("editUserTable").style.display = "none";
//            document.getElementById("editSearchBox").style.display = "none";
//        } else {
//            document.getElementById("editUserTable").style.display = "table";
//            document.getElementById("editSearchBox").style.display = "block";
//            document.getElementById("addUserTable").style.display = "none";
//        }
    };

    function validateRequest(){
        var valid = false;

//        $http.post('/projectValidate', {'projectNumbers': $scope.projectNumArray}).then(function(resp) {
//            if(resp.data === "true") {
//                valid = true;
//            }
//            if (valid === false) {
//                $scope.errorText = "Invalid Project Number";
//                return false;
//            }
//        }, function(err) {
//            console.error("project validate fail", err)
//        });

        if(!$scope.projectInfo.sponsorName || $scope.projectInfo.sponsorName.length <= 0) {
            $scope.errorText = "Sponsor name must not be empty";
            return false;
        }

        if(!$scope.projectInfo.projectName || $scope.projectInfo.projectName.length <= 0) {
            $scope.errorText = "Project name must not be empty";
            return false;
        }

        if(!$scope.projectInfo.membersEmails || $scope.projectInfo.membersEmails.length <= 0) {
            $scope.errorText = "Members emails must not be empty";
            return false;
        }

        if(!$scope.projectInfo.defaultBudget || $scope.projectInfo.defaultBudget.length <= 0) {
            $scope.errorText = "Budget must not be empty";
            return false;
        }

        $scope.errorText = "";
        return true;
    }

}]);
