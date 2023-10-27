// This code comes from https://github.com/LouisKlimek/HeadlessDetectJS
// The local modifications make debugging easier on the test interface.

class HeadlessDetect {
    allTestFunctions = ['testUserAgent', 'testChromeWindow', 'testPlugins', 'testAppVersion', 'testConnectionRtt'];

    constructor() {
    }



    //* All Tests *//

    // User Agent
    testUserAgent() {
        globalThis.user_agent = window.navigator.userAgent;
        if (/Headless/.test(window.navigator.userAgent)) {
            // Headless
            return 1;
        } else {
            // Not Headless
            return 0;
        }
    }

    // Window.Chrome
    testChromeWindow() {
        globalThis.eval_string = eval.toString();
        globalThis.eval_string_length = eval.toString().length;
        globalThis.is_win_chrome = window.chrome;
        if (eval.toString().length == 33 && !window.chrome) {
            // Headless
            return 1;
        } else {
            // Not Headless
            return 0;
        }
    }

    // Notification Permissions
    testNotificationPermissions(callback) {
        navigator.permissions.query({name:'notifications'}).then(function(permissionStatus) {
            globalThis.permission = Notification.permission;
            globalThis.permission_state = permissionStatus.state;
            if(Notification.permission === 'denied' && permissionStatus.state === 'prompt') {
                // Headless
                callback(1);
            } else {
                // Not Headless
                callback(0);
            }
        });
    }

    // No Plugins
    testPlugins() {
        let length = navigator.plugins.length;
        globalThis.plugins_length = length;

        return length === 0 ? 1 : 0;
    }

    // App Version
    testAppVersion() {
        let appVersion = navigator.appVersion;
        globalThis.nav_appversion = appVersion;

        return /headless/i.test(appVersion) ? 1 : 0;
    }

    // Connection Rtt
    testConnectionRtt() {
        let connection = navigator.connection;
        globalThis.connection = connection;
        let connectionRtt = connection ? connection.rtt : undefined;
        globalThis.connectionRtt = connectionRtt

        if (connectionRtt === undefined) {
            return 0; // Flag doesn't even exists so just return NOT HEADLESS
        } else {
            return connectionRtt === 0 ? 1 : 0;
        }
    }



    //* Main Functions *//

    getHeadlessScore() {
        let score = 0;
        let testsRun = 0;

        // Notification Permissions test has to be done using Callbacks
        // That's why it's done separately from all the other tests.
        this.testNotificationPermissions(function(v){
            score += v;
            testsRun++;
            document.getElementById("debug_perms").innerHTML = "<p>testNotificationPermissions: " + v + "</p>"; // This is only used for debugging
        });

        // Loop through all functions and add their results together

        for(let i = 0; i < this.allTestFunctions.length; i++){
            score += this[this.allTestFunctions[i]].apply();
            testsRun++;
            const para = document.createElement("p");
            const node = document.createTextNode(this.allTestFunctions[i] + ": " + this[this.allTestFunctions[i]].apply()); // This is only used for debugging
            para.appendChild(node)
            document.getElementById("debug_func").appendChild(para);
        }

        return score / testsRun;
    }
}
