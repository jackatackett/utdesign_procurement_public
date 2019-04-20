app.controller('EditUsersCtrl', ['$scope', '$location', '$http', 'dispatcher', function($scope, $location, $http, dispatcher) {

    $scope.fieldKeys = ["projectNumbers", "firstName", "lastName", "netID", "email", "course", "role"];
    $scope.fields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course", "Role"];
    $scope.editableKeys = ["projectNumbers", "firstName", "lastName", "netID", "course"];
    $scope.editableFields = ["Project Number", "First Name", "Last Name", "NetID", "Course"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Numbers", "First Name", "Last Name", "NetID", "Email", "Course", "Role"];
    $scope.sortTableBy = 'lastName';
    $scope.orderTableBy = 'ascending';
    $scope.numberOfPages = 1;
    $scope.currentPage = 1;
    $scope.pageNumberArray = [];
    $scope.projectNumbers = [];
    $scope.keywordSearch = {};

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
        //~ document.getElementById("editModal").style.display = "none";
        $("#editModal").hide();
    };

    $scope.saveUserEdit = function() {
        //need to validate input
        $http.post('/userEdit', {'_id': $scope.selectedUser._id, 'projectNumbers': $scope.selectedUser.projectNumbers, 'firstName':$scope.selectedUser.firstName, 'lastName':$scope.selectedUser.lastName, 'netID':$scope.selectedUser.netID, 'course':$scope.selectedUser.course}).then(function(resp) {
        }, function(err) {
            console.error("Error", err.data);
        });

        $scope.requery();
        $scope.closeEditBox();
    };

    $scope.deleteUser = function (e) {
        $http.post('/userRemove', {'_id': $scope.selectedUser._id}).then(function(resp) {
        }, function(err) {
            console.error("Error", err.data);
        });

        $scope.requery();
        $scope.closeEditBox();
    };

    $scope.changePage = function(pageNumber) {
        if (!($scope.keywordSearch.role == 'student' ||
              $scope.keywordSearch.role == 'manager' ||
              $scope.keywordSearch.role == 'admin')) {
            $scope.keywordSearch.role = undefined;
        }

        $http.post('/userData', {
            'sortBy': $scope.sortTableBy,
            'order':$scope.orderTableBy,
            'pageNumber': pageNumber-1,
            'keywordSearch': $scope.keywordSearch
        }).then(function(resp) {
            $scope.users = resp.data;
            $scope.pageNumber = pageNumber;
            $scope.updatePageNumberArray();
        }, function(err) {
            console.error("Error", err.data);
        });
    };

    $scope.prevPage = function() {
        if ($scope.pageNumber > 1) {
            $scope.changePage($scope.pageNumber-1)
        }
    }

    $scope.nextPage = function() {
        if ($scope.pageNumber < $scope.numberOfPages) {
            $scope.changePage($scope.pageNumber+1)
        }
    }

    $scope.firstPage = function() {
        $scope.changePage(1);
    }

    $scope.lastPage = function() {
        $scope.changePage($scope.numberOfPages);
    }

    $scope.requery = function() {
        $scope.repage();
        $scope.changePage($scope.pageNumber);
    }

    $scope.updatePageNumberArray = function() {
        var low = Math.max(1, $scope.pageNumber - 5);
        var high = Math.min(low + 9, $scope.numberOfPages);
        low = Math.min(low, Math.max(1, high - 10));

        $scope.pageNumberArray.length = 0;
        for (var x = low; x <= high; x++) {
            $scope.pageNumberArray.push(x);
        }
    }

    $scope.repage = function() {
        if (!($scope.keywordSearch.role == 'student' ||
              $scope.keywordSearch.role == 'manager' ||
              $scope.keywordSearch.role == 'admin')) {
            $scope.keywordSearch.role = undefined;
        }

        $http.post('/userPages', $scope.keywordSearch).then(function(resp) {
            $scope.numberOfPages = resp.data;
            $scope.updatePageNumberArray();
        }, function(err) {
            console.error("Error", err.data);
        });
    }

    $scope.toggleSort = function(keyword) {
        if (keyword == $scope.sortTableBy) {
            if($scope.orderTableBy == 'ascending') {
                $scope.orderTableBy = 'descending';
            } else {
                $scope.orderTableBy = 'ascending';
            }
        } else {
            $scope.sortTableBy = keyword;
            $scope.orderTableBy = 'ascending';
        }
        $scope.requery();
    }

    $scope.listProjectNumbers = function(nums) {
        if (!nums || !nums.length) {
            return "";
        }

        var numList = "";
        for (var i = 0; i < nums.length; i++) {
            numList += nums[i];
            if (i != (nums.length - 1)) {
                numList += ", ";
            }
        }
        return numList;
    }

    $scope.repage();
    $scope.changePage(1);


    dispatcher.on('bulkUserEnd', function() {
        $scope.requery();
    });

}]);
