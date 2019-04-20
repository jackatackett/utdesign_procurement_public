app.controller('AdminAddCosts', ['$scope', '$location', '$http', '$window', function($scope, $location, $http, $window) {

    $scope.fieldKeys = ["projectNumber", "amount", "comment"];
    $scope.fields = ["Project Number", "Amount", "Comment"];
    $scope.cost = {};
    $scope.errorText = "";

    $scope.userEmail = "";
    $http.post("/userInfo").then(function(resp) {
        $scope.userEmail = resp.data["email"];
        $scope.cost["actor"] = $scope.userEmail;
    }, function(err) {
        console.error("Error", err.data);
    });
    

    $scope.adminEmails = [];
    $http.post("/getAdminList").then(function(resp) {
        $scope.adminEmails = resp.data;
    }, function(err) {
        console.error("Error", err.data);
    });

    $scope.types = ["refund", "reimbursement", "new budget"];

    function validateInput() {
        for (var inputKey in $scope.fieldKeys) {
            var value = $("#newCost" + $scope.fieldKeys[inputKey]).val();
            if (value.trim().length <= 0) {
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
            $http.post("/addCost", {"projectNumber": +Number($scope.cost["projectNumber"]), "type": $scope.cost["type"], "amount": $scope.cost["amount"], "comment": $scope.cost["comment"], "actor": $scope.cost["actor"]}).then(function(resp) {
                alert("Success");
                $window.location.reload();
            }, function(err) {
                alert("Failure");
            });
        }
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
