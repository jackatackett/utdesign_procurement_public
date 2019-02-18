app.controller('VerifyCtrl', ['$scope', '$http', '$location', function($scope, $http, $location) {

    $scope.credentials = {uuid: $("#verifyUUID").html(), email: '', password: ''};
    $scope.confirmPassword = "";

    $scope.doVerify = function() {
        if ($scope.confirmPassword != $scope.credentials.password) {
            alert("Passwords must match.");
            return;
        }

        console.log($scope.credentials, $scope.id);
        $http.post('/userVerify', $scope.credentials).then(function(resp) {
            console.log("Verify success", resp);
        }, function(err) {
            console.log("Verify error", err);
        })
    }

}]);