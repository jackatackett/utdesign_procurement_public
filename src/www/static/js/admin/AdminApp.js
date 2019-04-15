var app = angular.module('AdminApp', []);
app.value('dispatcher', {

    callbacks: {},
    emit: function(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(function (callback) {
                callback(data);
            })
        }
    },

    on: function(event, callback) {
        if (!this.callbacks[event]) {
            this.callbacks[event] = [];
        }

        this.callbacks[event].push(callback);
    }

});
