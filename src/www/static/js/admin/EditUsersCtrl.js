app.controller('EditUsersCtrl', ['$scope', '$location', '$http', function($scope, $location, $http) {

    $scope.fieldKeys = ["projectNumbers", "firstName", "lastName", "netID", "email", "course", "role"];
    $scope.fields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course", "Role"];
    $scope.editableKeys = ["projectNumbers", "firstName", "lastName", "netID", "course"];
    $scope.editableFields = ["Project Number", "First Name", "Last Name", "NetID", "Course"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course", "Role"];
    $scope.sortTableBy = 'lastName';
    $scope.orderTableBy = 'ascending';
    $scope.numberOfPages = [];

    $scope.users = [];
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
        $scope.selectedUser[rowIdx] = rowIdx;
    };

    $scope.closeEditBox = function() {
        document.getElementById("editModal").style.display = "none";
    };

    $scope.saveUserEdit = function() {
        $http.post('/userEdit', {'_id': $scope.selectedUser._id, 'projectNumbers': $scope.selectedUser.projectNumbers, 'firstName':$scope.selectedUser.firstName, 'lastName':$scope.selectedUser.lastName, 'netID':$scope.selectedUser.netID, 'course':$scope.selectedUser.course}).then(function(resp) {
            console.log("userData success", resp);
        }, function(err) {
            console.error("Error", err.data);
        });

        $http.post('/userData', {'sortBy': $scope.sortTableBy, 'orderBy':$scope.orderTableBy}).then(function(resp) {
            console.log("userData success", resp);
            $scope.users = resp.data;
        }, function(err) {
            console.error("Error", err.data);
        });

        $scope.closeEditBox();
    };

    $scope.deleteUser = function (e) {
        console.log("remove user: " + $scope.selectedUser.firstName + " " + $scope.selectedUser.lastName);
        $http.post('/userRemove', {'_id': $scope.selectedUser._id}).then(function(resp) {
            console.log("userData success", resp);
        }, function(err) {
            console.error("Error", err.data);
        });

        $http.post('/userData', {'sortBy': $scope.sortTableBy, 'orderBy':$scope.orderTableBy}).then(function(resp) {
            console.log("userData success", resp);
            $scope.users = resp.data;
        }, function(err) {
            console.error("Error", err.data);
        });

        $scope.closeEditBox();
    };

    $scope.changePage = function() {
        console.log("change page");
    };

    $http.post('/userPages', {}).then(function(resp) {
        console.log("userPages success", resp);
        $scope.numberOfPages.length = 0;

        for (var i = 0; i < resp.data; i++)
            $scope.numberOfPages.push(i+1);

    }, function(err) {
        console.error("Error", err.data);
    });

    $http.post('/userData', {'sortBy': $scope.sortTableBy, 'orderBy':$scope.orderTableBy}).then(function(resp) {
        console.log("userData success", resp);
        $scope.users = resp.data;
    }, function(err) {
        console.error("Error", err.data);
    });

}]);