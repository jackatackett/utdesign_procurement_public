app.controller('SignInCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.credentials = {email: '', password: ''};

    $scope.doSignIn = function() {
        console.log($scope.credentials);
        $http.post('/userLogin', $scope.credentials).then(function(resp) {
            console.log("Login success", resp);
        }, function(err) {
            console.log("Login error", err);
        })
    }

}]);