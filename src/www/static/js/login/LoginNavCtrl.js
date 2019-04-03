app.controller('LoginNavCtrl', ['$scope', '$location', function($scope, $location) {

    //add a listener for the nav bar
    $scope.$on('$locationChangeSuccess', function() {
        // TODO What you want on the event.

        var hash = $location.hash();

//        if (hash == 'help') {
//            //show create
//            $("#signInCtrlDiv").hide();
//            $("#forgotPasswordCtrlDiv").hide();
////            $("#loginHelpDiv").show();
//
//        } else
        if (hash == 'forgotpassword') {
            //show status
            $("#signInCtrlDiv").hide();
            $("#forgotPasswordCtrlDiv").show();
//            $("#loginHelpDiv").hide();

        } else {
            //show help
            $("#signInCtrlDiv").show();
            $("#forgotPasswordCtrlDiv").hide();
//            $("#loginHelpDiv").hide();
        }

    });

}]);