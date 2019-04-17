app.controller('RequestSummaryCtrl', ['$scope', '$location', '$http', '$timeout', '$interval', 'dispatcher', 'statusLut', function($scope, $location, $http, $timeout, $interval, dispatcher, statusLut) {

    $scope.statusLut = statusLut;

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
            for (var item in data[d]["items"]) {
                result[d]["items"][item]["unitCost"] = convertCosts(data[d]["items"][item]["unitCost"]);
                result[d]["items"][item]["totalCost"] = convertCosts(data[d]["items"][item]["totalCost"]);
            }
            result[d]["requestTotal"] = convertCosts(data[d]["requestTotal"]);
            result[d]["shippingCost"] = convertCosts(data[d]["shippingCost"]);
        }
        return result;
    };

    $scope.fieldKeys = ["requestNumber", "projectNumber", "status", "vendor", "URL", "requestTotal", "shippingCost"];
    $scope.fields = ["Request Number", "Project Number", "Status", "Vendor", "URL", "Total Cost", "Shipping Cost"];
    $scope.itemFieldKeys = ["description", 'itemURL', "partNo", "quantity", "unitCost", "totalCost"];
    $scope.itemFields = ["Description", 'Item URL', "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Item Cost"];
    $scope.historyFields = ["Timestamp", "Source", "Comment", "Old State", "New State"];
    $scope.historyFieldKeys = ["timestamp", "actor", "comment", "oldState", "newState"];
    $scope.statuses = ["Pending Approval", "Unsubmitted", "Approved", "Rejected", "Pending Updates and Reapproval", "Pending Updates", "Ordered", "Ready for Pickup", "Picked Up"];
    $scope.statusesKeys = ["pending", "saved", "manager approved", "rejected", "updates for manager", "updates for admin", "ordered", "ready for pickup", "complete"];

    $scope.pageNumberArray = [];
    $scope.primaryFilter = {};
    $scope.secondaryFilter = {};
    $scope.sortTableBy = 'requestNumber';
    $scope.orderTableBy = 'ascending';

    $scope.data = [];

    $scope.adminComment = "";

    $scope.selectedStatuses = [];
    $scope.addToSelectedStatuses = function(status) {
        if ($scope.selectedStatuses.includes(status)) {
            var idx = $scope.selectedStatuses.indexOf(status);
            if (idx !== -1) $scope.selectedStatuses.splice(idx, 1);
        } else {
            $scope.selectedStatuses.push(status);
        }
        $scope.requery();
    };

    $scope.expanded = false;
    $scope.showCheckboxes = function() {
        var checkboxes = document.getElementById("checkboxes");
        if (!$scope.expanded) {
            checkboxes.style.display = "block";
            $scope.expanded = true;
        } else {
            checkboxes.style.display = "none";
            $scope.expanded = false;
        }
    }

    $scope.toggleCollapse = function(e) {
        var target = e.currentTarget;
        $(target.nextElementSibling).toggle();
    };

    $scope.rejectRequest = function(e, rowIdx) {
        $scope.adminComment = "";
        $("#rejectModal").show();
        currentRow = rowIdx;
    };

    $scope.permanentReject = function(e) {
        $http.post('/procurementRejectAdmin', {'_id':$scope.data[currentRow]._id, "comment": $scope.adminComment}).then(function(resp) {
            alert("Success!");
            $scope.adminComment = "";
            $scope.requery();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.adminComment = "";
            $scope.requery();
            $scope.closeRejectBox();
        });
    };

    $scope.sendForUpdatesAdmin = function(e) {
        $http.post('/procurementUpdateAdmin', {'_id':$scope.data[currentRow]._id, "comment": $scope.adminComment}).then(function(resp) {
            alert("Success!");
            $scope.adminComment = "";
            $scope.requery();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.adminComment = "";
            $scope.requery();
            $scope.closeRejectBox();
        });
    };

    $scope.sendForUpdatesManagerAdmin = function(e) {
        $http.post('/procurementUpdateManagerAdmin', {'_id':$scope.data[currentRow]._id, "comment": $scope.adminComment}).then(function(resp) {
            alert("Success!");
            $scope.adminComment = "";
            $scope.requery();
            $scope.closeRejectBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.adminComment = "";
            $scope.requery();
            $scope.closeRejectBox();
        });
    };

    $scope.closeRejectBox = function(e) {
        $scope.adminComment = "";
        $("#rejectModal").hide();
    };

    $scope.setShipping = function(e) {
        $http.post('/procurementOrder', {'_id':$scope.data[shippingRow]._id, "amount":$("#shippingAmt").val()}).then(function(resp) {
            alert("Success!");
            $scope.requery();
            $scope.cancelShippingBox();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.requery();
            $scope.cancelShippingBox();
        });
    }

    $scope.cancelShippingBox = function(e) {
        $("#shippingModal").hide();
    };

    $scope.orderRequest = function(e, rowIdx) {
        shippingRow = rowIdx;
        $("#shippingModal").show();
        
    };

    $scope.readyRequest = function(e, rowIdx) {
        $http.post('/procurementReady', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
            alert("Success!");
            $scope.requery();
        }, function(err) {
            console.error("Error", err.data)
            alert("Error");
            $scope.requery();
        });
    };

    $scope.completeRequest = function(e, rowIdx) {
        $http.post('/procurementComplete', {'_id':$scope.data[rowIdx]._id}).then(function(resp) {
            alert("Success!");
            $scope.requery();
        }, function(err) {
            console.error("Error", err.data);
            alert("Error");
            $scope.requery();
        });
    };

    $scope.canOrder = function(status) {
        return status == "manager approved";
    };

    $scope.canPickup = function(status) {
        return status == "ordered";
    };

    $scope.canComplete = function(status) {
        return status == "ready for pickup";
    };

    $scope.viewHistory = function(e, rowIdx) {
        $("#historyBody").empty();
        var historyHTML = "";
        for (var hist in $scope.data[rowIdx]["history"]) {
            historyHTML += '<tr style="border-bottom: 1.5px solid black">';
            for (var ele in $scope.historyFieldKeys) {
                if ($scope.historyFieldKeys[ele] == "oldState" || $scope.historyFieldKeys[ele] == "newState") {
                    historyHTML += '<td scope="col" style="background-color: #eee;">' + statusLut[$scope.data[rowIdx]["history"][hist][$scope.historyFieldKeys[ele]]] + '</td>';
                }
                else {
                    historyHTML += '<td scope="col" style="background-color: #eee;">' + $scope.data[rowIdx]["history"][hist][$scope.historyFieldKeys[ele]] + '</td>';
                }
            }
            historyHTML += '</tr>';
        }
        if (historyHTML == "") {
            historyHTML = "No history";
        }
        $("#historyBody").append(historyHTML);
        $("#historyModal").show();
    };

    $scope.closeHistoryBox = function(e) {
        $("#historyModal").hide();
    };

    $scope.editRequest = function(e, rowIdx) {
        $scope.selectedRequestInfo = $scope.data[rowIdx];
        dispatcher.emit("editRequest");
        $("#requestEditModal").show();
    };

    // ALL PAGE RELATED FUNCTIONS BELOW HERE

    $scope.changePage = function(pageNumber) {
        $http.post('/requestData', {
            'sortBy': $scope.sortTableBy,
            'order':$scope.orderTableBy,
            'pageNumber': pageNumber-1,
            'primaryFilter': $scope.primaryFilter,
            'secondaryFilter': $scope.secondaryFilter,
            'statusFilter': $scope.selectedStatuses
        }).then(function(resp) {
            $scope.data = cleanData(resp.data);
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
        $http.post('/requestPages', {
            primaryFilter: $scope.primaryFilter,
            secondaryFilter: $scope.secondaryFilter
        }).then(function(resp) {
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
    dispatcher.on("refreshStatuses", $scope.requery);


    // ALL GENERATING REPORTS CODE BELOW

    // set up the datepickers

    $('#reportStart').datepicker({
        weekStart: 1,
        daysOfWeekHighlighted: "6,0",
        autoclose: true,
        todayHighlight: true,
    });
    $('#reportStart').datepicker("setDate", new Date());

    $('#reportEnd').datepicker({
        weekStart: 1,
        daysOfWeekHighlighted: "6,0",
        autoclose: true,
        todayHighlight: true,
    });
    $('#reportEnd').datepicker("setDate", new Date());

    $scope.showGenerateReportsModal = function() {
        $("#generateReportsModal").show();
    }

    $scope.generateReport = function() {
        $http.post('/reportGenerate', {
            'sortBy': $scope.sortTableBy,
            'order':$scope.orderTableBy,
            'primaryFilter': $scope.primaryFilter,
            'secondaryFilter': $scope.secondaryFilter
        }).then(function(resp) {
            $scope.data = resp.data;

            $('<form></form>')
                 .attr('action', 'reportDownload/' + resp.data)
                 .appendTo('body').submit().remove();

        }, function(err) {
            console.error("Error", err.data);
        });
    }

    $scope.cancelReport = function() {
        $("#generateReportsModal").hide();
    }

    $scope.isEmpty = function(obj) {
        for (var x in obj) {
            if (obj.hasOwnProperty(x) && obj[x]) {
                return false;
            }
        }
        return true;
    }

}]);

