app.controller('AddUserBulkCtrl', ['$scope', 'dispatcher', '$location', '$http', '$window', function($scope, dispatcher, $location, $http, $window) {

    $scope.errorText = "";
    $scope.bulkKeys = ["projectNumbers", "firstName", "lastName", "netID", "email", "course", "role", "comment"];
    $scope.bulkFields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course", "Role", "Comment"];
    $scope.editableKeys = ["projectNumbers", "firstName", "lastName", "netID", "email", "course", 'role'];
    $scope.editableFields = ["Project Number", "First Name", "Last Name", "NetID", 'Email', "Course", 'Role'];
    $scope.numberOfPages = 1;
    $scope.currentPage = 1;
    $scope.pageNumberArray = [];
    $scope.users = [];
    $scope.filterStatus = "valid";
    $scope.metadata = {};
    $scope.selectedIdx = -1;

    $scope.bulkSubmit = function() {
        if ($scope.metadata.conflicting || $scope.metadata.invalid) {
            alert("Cannot submit with unresolved issues.");
        } else {
            $http.post('/userSpreadsheetSubmit').then(function(resp) {
                alert("Success!");
                $location.hash('editUsers');
                dispatcher.emit('bulkEnd');
            }, function(err) {
                alert("Error!");
                console.error(err);
            });
        }
    }

    $scope.changePage = function(pageNumber) {
        $http.post('/userSpreadsheetData', {
            'sortBy': $scope.sortTableBy,
            'order':$scope.orderTableBy,
            'pageNumber': pageNumber-1,
            'bulkStatus': $scope.filterStatus
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

    $scope.repage = function(toFirst) {
        $http.post('/userSpreadsheetPages', {
            'bulkStatus': $scope.filterStatus
        }).then(function(resp) {
            $scope.numberOfPages = resp.data;
            $scope.updatePageNumberArray();
            if (toFirst) {
                $scope.firstPage();
            }
        }, function(err) {
            console.error("Error", err.data);
        });
    }

    $scope.setFilterStatus = function(newStatus) {
        $scope.filterStatus = newStatus;
        $scope.requery();
    }

    $scope.metadataQuery = function() {
        $http.post('/userSpreadsheetMetadata').then(function(resp) {
            $scope.metadata = resp.data;
        });
    }

    $scope.revalidateUser = function(rowIdx, comparisonBox) {
        $http.post('/userSpreadsheetRevalidate', {
            'bulkStatus': $scope.filterStatus,
            'index': rowIdx,
            'user': comparisonBox ? $scope.compareUserNew : $scope.users[rowIdx]
        }).then(function(resp) {
            if ($scope.filterStatus != resp.data.status) {
                $scope.metadata[$scope.filterStatus]--;
                $scope.metadata[resp.data.status]++;
                $scope.users[rowIdx] = null;
            } else {
                $scope.users[rowIdx] = resp.data.user;
            }

            if (comparisonBox) {
                $scope.compareUserNew = resp.data.user;
            }

        }, function(err) {
            alert("Error during revalidation.");
        });
    }

    $scope.showCompare = function(rowIdx) {
        $http.post("/userSingleData", {
            email: $scope.users[rowIdx].email
        }).then(function(resp) {
            $scope.selectedIdx = rowIdx;
            $scope.compareUserNew = JSON.parse(JSON.stringify($scope.users[rowIdx]));
            $scope.compareUserOld = resp.data;
            $("#compareModal").show();
        }, function(err) {
            alert("Error retrieving user comparison data.")
        });

    }

    $scope.exitCompare = function(rowIdx) {
        $("#compareModal").hide();
    }

    $scope.isBadCell = function(user, fieldK) {
        return !user || (
            (fieldK == 'projectNumbers' && user.comment.missingProjects.length) ||
            (fieldK == 'role' && user.comment.invalidRole) ||
            (user.comment.missingAttributes.indexOf(fieldK) >= 0) ||
            (user.comment.conflictingAttributes.indexOf(fieldK) >= 0)
        )
    }

    dispatcher.on('bulkRefresh', function() {
       $scope.repage(true);
       $scope.metadataQuery();
    });

}]);
