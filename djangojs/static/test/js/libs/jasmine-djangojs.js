/**
    Jasmine Reporter that outputs TAP test results to the browser console.
    Useful for running in a headless environment such as PhantomJs, ZombieJs etc.

    Usage:
    // From your html file that loads jasmine:
    jasmine.getEnv().addReporter(new jasmine.TapReporter());
    jasmine.getEnv().execute();
*/

(function(jasmine, console) {
    if (!jasmine) {
        throw "jasmine library isn't loaded!";
    }

    var INDENT = 4,
        PHANTOM_STACK_REGEX = /^\s+at\s+(.*):(\d+)$/,
        BROWSER_STACK_REGEX = /^\s+at\s+(.*)\s+\((.*):(\d+):(\d+)\)$/;

    var TapReporter = function() {
        if (!console || !console.log) { throw "console isn't present!"; }
        this.indent = '';
    };

    var proto = TapReporter.prototype;

    proto.reportRunnerStarting = function(runner) {
        this.start_time = (new Date()).getTime();
        this.executed_specs = 0;
        this.passed_specs = 0;
        this.suite_assertions = 0;
        this.modules = [];
    };

    proto.reportRunnerResults = function(runner) {
        var failed = this.executed_specs - this.passed_specs;
        var spec_str = this.executed_specs + (this.executed_specs === 1 ? " spec, " : " specs, ");
        var fail_str = failed + (failed === 1 ? " failure in " : " failures in ");
        var color = (failed > 0)? "red" : "green";
        var dur = (new Date()).getTime() - this.start_time;

        this.log(spec_str + fail_str + (dur/1000) + "s.", color);
    };


    proto.reportSpecStarting = function(spec) {
        this.updateModule(spec);
        this.log(this.indent + '# test: ' + spec.description);
        this.executed_specs++;
    };

    proto.reportSpecResults = function(spec) {
        var results = spec.results(),
            items = results.getItems();

        if (results.passed()) {
            this.passed_specs++;
        }

        for (var i = 0; i < items.length; i++) {
            var result = items[i],
                trace = items[i].trace.stack || items[i].trace;

            this.suite_assertions++;

            if (result.passed()) {
                console.log(this.indent + 'ok ' + this.suite_assertions);
            } else {
                output = this.indent + 'not ok ' + this.suite_assertions;
                output += " - expected: '" + result.expected + "', got: '" + result.actual + "'";
                if (result.matcherName) {
                    output += ", matcher: '" + result.matcherName + "'";
                }
                this.logStack(result, output);
            }
        }
    };

    proto.logStack = function(result, out) {
        var stack = result.trace.stack;
        if (stack) {
            lines = stack.split('\n');
            if (lines && /^\w*Error:/.test(lines[0]) && lines.length > 2) {
                if (navigator.userAgent.indexOf('PhantomJS') != -1) {
                    this.phantomStack(lines, output);
                } else {
                    this.browserStack(lines, output);
                }
            }
        } else {
            console.log(output);
        }
    };

    proto.phantomStack = function(lines, output) {
        var match = PHANTOM_STACK_REGEX.exec(lines[1]);
        console.log(output + ', source: at ' + match[1] + ':' + match[2] );
        for (var i=2; i < lines.length ; i++) {
            match = PHANTOM_STACK_REGEX.exec(lines[i]);
            console.log(this.indent + '#    at ' + match[1] + ':' + match[2] );
        }
    };

    proto.browserStack = function(lines, output) {
        var match = BROWSER_STACK_REGEX.exec(lines[1]);
        console.log(output + ', source: at ' + match[2] + ':' + match[3] );
        for (var i=2; i < lines.length ; i++) {
            match = BROWSER_STACK_REGEX.exec(lines[i]);
            console.log(this.indent + '#    at ' + match[2] + ':' + match[3] );
        }
    };

    proto.updateModule = function(spec) {
        modules = this.getModules(spec);
        for (var i=0; i < modules.length; i++) {
            if (i < this.modules.length) {
                if (modules[i] === this.modules[i]) {
                    continue;
                } else {
                    this.modules.length = i;
                }
            }
            this.modules.push(modules[i]);
            this.indent = '';
            for (var j=0; j < Math.max(0, this.modules.length - 1) * INDENT; j++) {
                this.indent += ' ';
            }
            console.log(this.indent + '# module: ', modules[i]);
        }
    };

    proto.getModules = function(item) {
        var modules = [];
        if (item.suite) {
            modules = modules.concat(this.getModules(item.suite));
        }
        else if (item.parentSuite) {
            modules = modules.concat(this.getModules(item.parentSuite));
        }
        if (item.hasOwnProperty('parentSuite')) {
            modules.push(item.description);
        }
        return modules;
    };

    proto.reportSuiteResults = function(suite) {
        if (!suite.parentSuite) { return; }
        var results = suite.results();
        var failed = results.totalCount - results.passedCount;
        var color = (failed > 0)? "red" : "green";
        // this.log(suite.description + ": " + results.passedCount + " of " + results.totalCount + " passed.", color);
        // this.log('1..' + this.suite_assertions);

    };

    proto.log = function(str, color) {
        var text = (color !== undefined && this.showColors)? ANSI.colorize_text(str, color) : str;
        console.log(text);
    };

    jasmine.TapReporter = TapReporter;
})(jasmine, console);

