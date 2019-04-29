app.controller('EditProjectsCtrl', ['$scope', '$location', '$http', 'dispatcher', function($scope, $location, $http, dispatcher) {

    $scope.fieldKeys = ["projectNumber", "sponsorName", "projectName", "membersEmails", "defaultBudget"];
    $scope.fields = ["Project Number", "Sponsor Name", "Project Name", "Members Emails", "Budget"];
    $scope.editableKeys = ["sponsorName", "projectName", "membersEmails"];
    $scope.editableFields = ["Sponsor Name", "Project Name", "Members Emails"];
    $scope.grid = [];
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

    function convertCosts(value) {
        if (typeof value === "undefined") {
            return "$0.00";
        }
        value = String(value);
        if (value !== "undefined") {
            while (value.length < 3) {
                value = "0" + value;
            }
            return "$" + value.slice(0, -2) + "." + value.slice(value.length-2);
        }
        return "$0.00"
    };

    function cleanData(data) {
        var result = [];
        for (var d in data) {
            result[d] = data[d];
            result[d]["defaultBudget"] = convertCosts(data[d]["defaultBudget"]);
        }
        return result;
    };

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
        //console.log($scope.selectedProject.membersEmails);
        $http.post('/projectEdit', {'projectNumber': Number($scope.selectedProject.projectNumber), 'sponsorName':$scope.selectedProject.sponsorName, 'projectName':$scope.selectedProject.projectName, 'membersEmails':$scope.selectedProject.membersEmails.split(",")}).then(function(resp) {
            alert("Success!");
        }, function(err) {
            console.error("Error", err.data);
        });

        $scope.requery();
        $scope.closeEditBox();
    };

    $scope.deleteProject = function (e) {
        $http.post('/projectInactivate', {'_id': $scope.selectedProject._id}).then(function(resp) {
            alert("Success!");
        }, function(err) {
            console.error("Error", err.data);
        });

        $scope.requery();
        $scope.closeEditBox();
    };

    $scope.changePage = function(pageNumber) {
        $http.post('/projectData', {
            'sortBy': $scope.sortTableBy,
            'order':$scope.orderTableBy,
            'pageNumber': pageNumber-1,
            'keywordSearch': $scope.keywordSearch
        }).then(function(resp) {
            $scope.projects = cleanData(resp.data);
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
        if ($scope.keywordSearch.defaultBudget) {
            $scope.keywordSearch.defaultBudget = String($scope.keywordSearch.defaultBudget);
        }

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
        $http.post('/projectPages', $scope.keywordSearch).then(function(resp) {
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

    $scope.repage();
    $scope.changePage(1);

    dispatcher.on('bulkProjectEnd', function() {
        $scope.requery();
    });

}]);
