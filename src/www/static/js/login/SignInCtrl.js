app.controller('SignInCtrl', ['$scope', '$http', '$window', function($scope, $http, $window) {

    $scope.credentials = {email: '', password: ''};

    $scope.doSignIn = function() {
        console.log($scope.credentials);
        $http.post('/userLogin', $scope.credentials).then(function(resp) {
            console.log("Login success", resp);
            $window.location.href = '/';
        }, function(err) {
            console.log("Login error", err);
        })
    }

}]);