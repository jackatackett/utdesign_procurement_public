app.controller('EditProjectsCtrl', ['$scope', '$location', '$http', function($scope, $location, $http) {

    $scope.fieldKeys = ["projectNumber", "sponsorName", "projectName", "membersEmails", "defaultBudget"];
    $scope.fields = ["Project Number", "Sponsor Name", "Project Name", "Members Emails", "Budget"];
    $scope.editableKeys = ["sponsorName", "projectName", "membersEmails", "defaultBudget"];
    $scope.editableFields = ["Sponsor Name", "Project Name", "Members Emails", "Budget"];
    $scope.grid = [];
    $scope.itemFieldKeys = ["description", "partNo", "quantity", "unitCost", "total"];
    $scope.itemFields = ["Description", "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"];
    $scope.columns = ["Project Number", "Sponsor Name", "Project Name", "Members Emails", "Budget"];
    $scope.sortTableBy = 'projectNumber';
    $scope.orderTableBy = 'ascending';
    $scope.numberOfPages = 1;
    $scope.currentPage = 1;
    $scope.pageNumberArray = [];
    $scope.projectNumbers = [];
    $scope.keywordSearch = {};

    $scope.projects = [];
    $scope.selectedProject = {};

    $scope.editProject = function(e, rowIdx) {
        $("#editProjectModal").show();
        $scope.selectedProject = {};
        var proj = $scope.projects[rowIdx];
        for (var key in proj) {
            if (proj.hasOwnProperty(key)) {
                $scope.selectedProject[key] = proj[key];
            }
        }
        $scope.selectedProject[rowIdx] = rowIdx;
    };

    $scope.closeEditBox = function() {
        $("#editProjectModal").hide();
    };

    $scope.saveProjectEdit = function() {
        //need to validate input
//        $http.post('/userEdit', {'_id': $scope.selectedUser._id, 'projectNumbers': $scope.selectedUser.projectNumbers, 'firstName':$scope.selectedUser.firstName, 'lastName':$scope.selectedUser.lastName, 'netID':$scope.selectedUser.netID, 'course':$scope.selectedUser.course}).then(function(resp) {
//        }, function(err) {
//            console.error("Error", err.data);
//        });

        $scope.requery();
        $scope.closeEditBox();
    };

    $scope.deleteProject = function (e) {
//        $http.post('/userRemove', {'_id': $scope.selectedUser._id}).then(function(resp) {
//            console.log("userData success", resp);
//        }, function(err) {
//            console.error("Error", err.data);
//        });

        $scope.requery();
        $scope.closeEditBox();
    };

    $scope.changePage = function(pageNumber) {
        if (!($scope.keywordSearch.role == 'student' ||
              $scope.keywordSearch.role == 'manager' ||
              $scope.keywordSearch.role == 'admin')) {
            $scope.keywordSearch.role = undefined;
        }

        $http.post('/projectData', {
            'sortBy': $scope.sortTableBy,
            'order':$scope.orderTableBy,
            'pageNumber': pageNumber-1,
            'keywordSearch': $scope.keywordSearch
        }).then(function(resp) {
            $scope.projects = resp.data;
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
//        if (!($scope.keywordSearch.role == 'student' ||
//              $scope.keywordSearch.role == 'manager' ||
//              $scope.keywordSearch.role == 'admin')) {
            $scope.keywordSearch.role = undefined;
        //}

        $http.post('/projectPages', $scope.keywordSearch).then(function(resp) {
            $scope.numberOfPages = resp.data;
            $scope.updatePageNumberArray();
        }, function(err) {
            console.error("Error", err.data);
        });
    }

    $scope.toggleSort = function(keyword) {
        console.log(keyword);
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

    $scope.repage();
    $scope.changePage(1);

}]);
