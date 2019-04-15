app.controller('VerifyCtrl', ['$scope', '$http', '$location', function($scope, $http, $location) {

    $scope.credentials = {uuid: $("#verifyUUID").html(), email: '', password: ''};
    $scope.confirmPassword = "";

    $scope.doVerify = function() {
        if ($scope.confirmPassword != $scope.credentials.password) {
            alert("Passwords must match.");
            return;
        }

        $http.post('/userVerify', $scope.credentials).then(function(resp) {
            alert("Success!");
            window.location = '/'
        }, function(err) {
            if (err.status == 403) {
                alert("Incorrect email", err);
            } else {
                alert("Infrastructure error.");
                console.error("userVerify failed", err);
            }
        })
    }

}]);