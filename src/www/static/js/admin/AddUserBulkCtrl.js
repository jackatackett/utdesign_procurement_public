app.controller('AddUserBulkCtrl', ['$scope', 'dispatcher', '$location', '$http', '$window', function($scope, dispatcher, $location, $http, $window) {

    $scope.errorText = "";
    $scope.bulkKeys = ["projectNumbers", "firstName", "lastName", "netID", "email", "course", "role", "comment"];
    $scope.bulkFields = ["Project Number", "First Name", "Last Name", "NetID", "Email", "Course", "Role", "Comment"];
    $scope.numberOfPages = 1;
    $scope.currentPage = 1;
    $scope.pageNumberArray = [];
    $scope.users = [];
    $scope.filterStatus = "valid";
    $scope.metadata = {};

    $scope.submitBulk = function() {
        $http.post('/userSpreadsheetAdd').then(function(resp) {
            alert('Success!');
            $scope.hideBulk();
        }, function(err) {
            alert('Error!');
            $scope.hideBulk();
        });
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

    $scope.revalidateUser = function(rowIdx) {
        $http.post('/userSpreadsheetRevalidate', {
            'bulkStatus': $scope.filterStatus,
            'index': rowIdx,
            'user': $scope.users[rowIdx]
        }).then(function(resp) {
            $scope.users[rowIdx] = resp.data;
        }, function(err) {
            alert("Error during revalidation.");
            console.log(err);
        });
    }

    dispatcher.on('bulkRefresh', function() {
       $scope.repage(true);
       $scope.metadataQuery();
    });

}]);
