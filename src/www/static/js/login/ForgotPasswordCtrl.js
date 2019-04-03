app.controller('ForgotPasswordCtrl', ['$scope', '$http', '$window', function($scope, $http, $window) {

    $scope.credentials = {email: ''};

    $scope.doForgotPassword = function() {
        console.log($scope.credentials);
        $http.post('/userForgotPassword', $scope.credentials).then(function(resp) {
            console.log("Password recovery success", resp);
            $window.location.href = '/';
            alert("Success! Please check your email for the recovery link.");
        }, function(err) {
            console.log("Password recovery error", err);
            alert("Error!");
        })
    }

}]);