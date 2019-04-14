app.controller('AddProjectsCtrl', ['$scope', '$location', '$http', '$window', function($scope, $location, $http, $window) {

    $scope.errorText = "";
    $scope.fieldKeys = ["projectNumber", "sponsorName", "projectName", "membersEmails"];
    $scope.fields = ["Project Number", "Sponsor Name", "Project Name", "Members Emails"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number(s)", "First Name", "Last Name", "NetID", "Email", "Course"];
    $scope.projectInfo = {'defaultBudget':'2000.00'};
    $scope.projectNumArray = [];
    $scope.membersEmails = [];

    $scope.users = [];

    $scope.addProject = function(e) {
        var target = e.currentTarget;

        if($scope.projectInfo.membersEmails) {
            $scope.membersEmails = $scope.projectInfo.membersEmails.replace(' ', '').split(',');
        }

        if($scope.projectInfo.defaultBudget) {
            if(!($scope.projectInfo.defaultBudget.includes("."))) {
                $scope.projectInfo.defaultBudget = $scope.projectInfo.defaultBudget + ".00";
            }
        }

        if(!validateRequest()) {
            console.log("request was invalid");
        } else {
            $http.post('/projectAdd', {'projectNumber':Number($scope.projectInfo.projectNumber), 'sponsorName':$scope.projectInfo.sponsorName, 'projectName':$scope.projectInfo.projectName, 'membersEmails':$scope.membersEmails, 'defaultBudget':$scope.projectInfo.defaultBudget, 'availableBudget':$scope.projectInfo.defaultBudget, 'pendingBudget':$scope.projectInfo.defaultBudget}).then(function(resp) {
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

        if(!$scope.projectInfo.sponsorName || $scope.projectInfo.sponsorName.length <= 0) {
            $scope.errorText = "Sponsor name must not be empty";
            return false;
        }

        if(!$scope.projectInfo.projectName || $scope.projectInfo.projectName.length <= 0) {
            $scope.errorText = "Project name must not be empty";
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
