var app = angular.module('StudentApp', []);
app.value('dispatcher', {

    callbacks: {},
    publish: function(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(function (callback) {
                callback(data);
            })
        }
    },

    subscribe: function(event, callback) {
        if (!this.callbacks[event]) {
            this.callbacks[event] = [];
        }

        this.callbacks[event].push(callback);
    }

});