app.controller('AdminAddCosts', ['$scope', '$location', '$http', '$window', function($scope, $location, $http, $window) {

    $scope.fieldKeys = ["projectNumber", "amount", "comment"];
    $scope.fields = ["Project Number", "Amount", "Comment"];
    $scope.cost = {};
    $scope.errorText = "";

    $scope.userEmail = "";
    $http.post("/userInfo").then(function(resp) {
        $scope.userEmail = resp.data["email"];
        console.log($scope.userEmail);
        $scope.cost["actor"] = $scope.userEmail;
        console.log($scope.cost);
    }, function(err) {
        console.log("Error", err.data);
    });
    

    $scope.adminEmails = [];
    $http.post("/getAdminList").then(function(resp) {
        $scope.adminEmails = resp.data;
    }, function(err) {
        console.log("Error", err.data);
    });

    $scope.types = ["refund", "reimbursement", "funding", "cut"];

    //~ var selectHTML = '<select id="newCosttype">';
    //~ for (var val in $scope.types) {
        //~ selectHTML += "<option value=" + $scope.types[val] + ">" + $scope.types[val] + "</option>";
    //~ }
    //~ selectHTML += "</select>";

    //~ $("#newCosttype").replaceWith(selectHTML);

    function validateInput() {
        for (var inputKey in $scope.fieldKeys) {
            var value = $("#newCost" + $scope.fieldKeys[inputKey]).val();
            console.log(inputKey, value);
            if (value.trim().length <= 0) {
                //~ $scope.errorText = "Field " + $("#newCost" + $scope.fieldKeys[inputKey]).parent().prev().html() + " should not be empty";
                $scope.errorText = $scope.fields[inputKey] + " should not be empty";
                return false;
            }
            //project number must be integer
            if ($scope.fieldKeys[inputKey] == "projectNumber" && !Number.isInteger(+value)) {
                $scope.errorText = "Project Number should be an integer";
                return false;
            }
            //amount must be at most 2 past the decimal
            if ($scope.fieldKeys[inputKey] == "amount" && Math.abs(Math.round(value*100) - value*100) >= .1) {
                $scope.errorText = "Amount should be a dollar amount";
                return false;
            }
        }
        //type must be either: refund, reimbursement, funding, cut
        //~ console.log($scope.cost);
        if ($scope.types.indexOf($scope.cost["type"]) < 0) {
            $scope.errorText = "Type must not be empty";
            return false;
        }
        //actor must not be empty
        if ($scope.adminEmails.indexOf($scope.cost["actor"]) < 0) {
            $scope.errorText = "Assignee must not be empty";
            return false;
        }
        $scope.errorText = "";
        return true;
    };

    $scope.addCost = function(e) {
        var target = e.currentTarget;

        //validate input
        if (validateInput()) {
            console.log($scope.cost);
            //post
            $http.post("/addCost", {"projectNumber": +Number($scope.cost["projectNumber"]), "type": $scope.cost["type"], "amount": $scope.cost["amount"], "comment": $scope.cost["comment"], "actor": $scope.cost["actor"]}).then(function(resp) {
                alert("Success");
                $window.location.reload();
            }, function(err) {
                alert("Failure");
            });
        }

        //~ var prjNumsAry = $scope.userInfo.projectNumbers.replace(' ', '').split(',');
        //~ for(var n in prjNumsAry) {
            //~ prjNumsAry[n] = Number(prjNumsAry[n]);
        //~ }

        //~ $http.post('/userAdd', {'projectNumbers':prjNumsAry, 'firstName':$scope.userInfo.firstName, 'lastName':$scope.userInfo.lastName, 'netID':$scope.userInfo.netID, 'email':$scope.userInfo.email, 'course':$scope.userInfo.course, 'role':'student'}).then(function(resp) {
            //~ console.log("Success", resp);
            //~ alert("Success!");
            //~ $window.location.reload();
        //~ }, function(err) {
            //~ console.error("Error", err.data);
            //~ alert("Error")
        //~ });
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
