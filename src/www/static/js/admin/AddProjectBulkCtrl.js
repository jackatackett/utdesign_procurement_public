app.controller('AddProjectBulkCtrl', ['$scope', 'dispatcher', '$location', '$http', '$window', function($scope, dispatcher, $location, $http, $window) {

    $scope.errorText = "";
    $scope.bulkKeys = ["projectNumber", "sponsorName", "projectName", "defaultBudget", "comment"];
    $scope.bulkFields = ["Project Number", "Sponsor Name", "Project Name", "Starting Budget", "Comment"];
    $scope.editableKeys = ["projectNumber", "sponsorName", "projectName", "defaultBudget"];
    $scope.editableFields = ["Project Number", "Sponsor Name", "Project Name", "Starting Budget"];
    $scope.numberOfPages = 1;
    $scope.currentPage = 1;
    $scope.pageNumberArray = [];
    $scope.projects = [];
    $scope.filterStatus = "valid";
    $scope.metadata = {};
    $scope.selectedIdx = -1;

    $scope.bulkSubmit = function() {
        if ($scope.metadata.conflicting || $scope.metadata.invalid) {
            alert("Cannot submit with unresolved issues.");
        } else {
            $http.post('/projectSpreadsheetSubmit').then(function(resp) {
                alert("Success!");
                $location.hash('editProjects');
                dispatcher.emit('bulkProjectEnd');
            }, function(err) {
                alert("Error!");
                console.error(err);
            });
        }
    }

    $scope.changePage = function(pageNumber) {
        $http.post('/projectSpreadsheetData', {
            'sortBy': $scope.sortTableBy,
            'order':$scope.orderTableBy,
            'pageNumber': pageNumber-1,
            'bulkStatus': $scope.filterStatus
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
        $http.post('/projectSpreadsheetPages', {
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
        $http.post('/projectSpreadsheetMetadata').then(function(resp) {
            $scope.metadata = resp.data;
        });
    }

    $scope.revalidateProject = function(rowIdx, comparisonBox) {
        $http.post('/projectSpreadsheetRevalidate', {
            'bulkStatus': $scope.filterStatus,
            'index': rowIdx,
            'project': comparisonBox ? $scope.compareProjectNew : $scope.projects[rowIdx]
        }).then(function(resp) {
            if ($scope.filterStatus != resp.data.status) {
                $scope.metadata[$scope.filterStatus]--;
                $scope.metadata[resp.data.status]++;
                $scope.projects[rowIdx] = null;
            } else {
                $scope.projects[rowIdx] = cleanProject(resp.data.project);
            }

            if (comparisonBox) {
                $scope.compareProjectNew = cleanProject(resp.data.project);
            }

        }, function(err) {
            alert("Error during revalidation.");
        });
    }

    $scope.markOverwrite = function(rowIdx, comparisonBox) {
        $http.post('/projectSpreadsheetOverwrite', {
            'projectNumber': $scope.projects[rowIdx].projectNumber,
        }).then(function(resp) {

            $scope.revalidateProject(rowIdx, comparisonBox);
            $scope.exitCompare();

        }, function(err) {
            alert("Error while marking project for overwrite.");
        });
    }

    $scope.showCompare = function(rowIdx) {
        $http.post("/projectSingleData", {
            projectNumber: $scope.projects[rowIdx].projectNumber
        }).then(function(resp) {
            $scope.selectedIdx = rowIdx;
            $scope.compareProjectNew = JSON.parse(JSON.stringify($scope.projects[rowIdx]));
            $scope.compareProjectOld = cleanProject(resp.data);
            $("#compareProjectsModal").show();
        }, function(err) {
            alert("Error retrieving project comparison data.")
        });

    }

    $scope.exitCompare = function() {
        $("#compareProjectsModal").hide();
    }

    $scope.isBadCell = function(project, fieldK) {
        return !project || (project.comment.missingAttributes.indexOf(fieldK) >= 0);
    }

    dispatcher.on('bulkProjectRefresh', function() {
       $scope.repage(true);
       $scope.metadataQuery();
    });

    function convertCosts(value) {
        if (typeof value === "undefined") {
            return "0.00";
        }
        value = String(value);
        if (value !== "undefined") {
            while (value.length < 3) {
                value = "0" + value;
            }
            return value.slice(0, -2) + "." + value.slice(value.length-2);
        }
        return "0.00";
    };

    function cleanProject(project) {
        project["defaultBudget"] = convertCosts(project["defaultBudget"]);
        return project;
    };

    function cleanData(data) {
        for (var d in data) {
            data[d]["defaultBudget"] = convertCosts(data[d]["defaultBudget"]);
        }
        return data;
    };

}]);
