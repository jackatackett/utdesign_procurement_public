app.controller('SignInCtrl', ['$scope', '$http', '$window', function($scope, $http, $window) {

    $scope.credentials = {email: '', password: ''};

    $scope.doSignIn = function() {
        $http.post('/userLogin', $scope.credentials).then(function(resp) {
            $window.location.href = '/';
        }, function(err) {
            alert("Login failure");
        })
    }

}]);