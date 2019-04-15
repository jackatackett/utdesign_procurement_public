app.controller('ForgotPasswordCtrl', ['$scope', '$http', '$window', function($scope, $http, $window) {

    $scope.credentials = {email: ''};

    $scope.doForgotPassword = function() {
        $http.post('/userForgotPassword', $scope.credentials).then(function(resp) {
            $window.location.href = '/';
            alert("Success! Please check your email for the recovery link.");
        }, function(err) {
            console.error("Password recovery error", err);
            alert("Error!");
        })
    }

}]);