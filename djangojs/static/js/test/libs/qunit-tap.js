/**
 * QUnit-TAP - A TAP Output Producer Plugin for QUnit
 *
 * https://github.com/twada/qunit-tap
 * version: 1.2.1
 *
 * Copyright (c) 2010, 2011, 2012 Takuto Wada
 * Dual licensed under the MIT and GPLv2 licenses.
 *   https://raw.github.com/twada/qunit-tap/master/MIT-LICENSE.txt
 *   https://raw.github.com/twada/qunit-tap/master/GPL-LICENSE.txt
 *
 * A part of extend function is:
 *   Copyright 2012 jQuery Foundation and other contributors
 *   Released under the MIT license.
 *   http://jquery.org/license
 *
 * A part of stripTags function is:
 *   Copyright (c) 2005-2010 Sam Stephenson
 *   Released under the MIT license.
 *   http://prototypejs.org
 *
 * @param qunitObject QUnit object reference.
 * @param printLikeFunction print-like function for TAP output (assumes line-separator is added by this function for each call).
 * @param options configuration options to customize default behavior.
 */
var qunitTap = function qunitTap(qunitObject, printLikeFunction, options) {
    'use strict';
    var qunitTapVersion = '1.2.1',
        detailsExtractor,
        tap = {},
        qu = qunitObject;

    if (!qu) {
        throw new Error('should pass QUnit object reference. Please check QUnit\'s "require" path if you are using Node.js (or any CommonJS env).');
    }
    if (typeof printLikeFunction !== 'function') {
        throw new Error('should pass print-like function');
    }
    if (typeof qu.tap !== 'undefined') {
        return;
    }

    // borrowed from qunit.js
    var extend = function (a, b) {
        var prop;
        for (prop in b) {
            if (b.hasOwnProperty(prop)) {
                if (typeof b[prop] === 'undefined') {
                    delete a[prop];
                } else {
                    a[prop] = b[prop];
                }
            }
        }
        return a;
    };

    // option deprecation and fallback function
    var deprecateOption = function (optionName, fallback) {
        if (!options || typeof options !== 'object') {
            return;
        }
        if (typeof options[optionName] === 'undefined') {
            return;
        }
        printLikeFunction('# WARNING: Option "' + optionName + '" is deprecated and will be removed in future version.');
        fallback(options[optionName]);
    };

    tap.config = extend(
        {
            initialCount: 1,
            noPlan: false,
            showModuleNameOnFailure: true,
            showTestNameOnFailure: true,
            showExpectationOnFailure: true,
            showSourceOnFailure: true
        },
        options
    );
    deprecateOption('count', function (count) {
        tap.config.initialCount = (count + 1);
    });
    deprecateOption('showDetailsOnFailure', function (flag) {
        tap.config.showModuleNameOnFailure = flag;
        tap.config.showTestNameOnFailure = flag;
        tap.config.showExpectationOnFailure = flag;
        tap.config.showSourceOnFailure = flag;
    });
    tap.VERSION = qunitTapVersion;
    tap.puts = printLikeFunction;
    tap.count = tap.config.initialCount - 1;

    var isPassed = function (details) {
        return !!(details.result);
    };

    var isFailed = function (details) {
        return !(isPassed(details));
    };

    // borrowed from prototype.js
    // not required since QUnit.log receives raw data (details). see jquery/qunit@c2cde34
    var stripTags = function (str) {
        if (!str) {
            return str;
        }
        return str.replace(/<\w+(\s+("[^"]*"|'[^']*'|[^>])+)?>|<\/\w+>/gi, '');
    };

    var escapeLineEndings = function (str) {
        return str.replace(/(\r?\n)/g, '$&# ');
    };

    var ltrim = function (str) {
        return str.replace(/^\s+/, '');
    };

    var quote = function (obj) {
        return '\'' + obj + '\'';
    };

    var noop = function (obj) {
        return obj;
    };

    var appendTo = function (desc, detailValue, fieldName, configName, formatter) {
        if (tap.config[configName] && typeof detailValue !== 'undefined') {
            desc.push(fieldName + ': ' + formatter(detailValue));
        }
    };

    var formatDetails = function (details) {
        if (isPassed(details)) {
            return details.message;
        }
        var desc = [];
        if (details.message) {
            desc.push(details.message);
        }
        appendTo(desc, details.expected, 'expected', 'showExpectationOnFailure', quote);
        appendTo(desc, details.actual, 'got', 'showExpectationOnFailure', quote);
        appendTo(desc, details.name, 'test', 'showTestNameOnFailure', noop);
        appendTo(desc, details.module, 'module', 'showModuleNameOnFailure', noop);
        appendTo(desc, details.source, 'source', 'showSourceOnFailure', ltrim);
        return desc.join(', ');
    };

    var formatTestLine = function (testLine, rest) {
        if (!rest) {
            return testLine;
        }
        return testLine + ' - ' + escapeLineEndings(rest);
    };

    var setupExtractor = function (logArguments) {
        switch (logArguments.length) {
        case 1:  // details
            detailsExtractor = function (args) { return args[0]; };
            break;
        case 2:  // result, message(with tags)
            detailsExtractor = function (args) { return {result: args[0], message: stripTags(args[1])}; };
            break;
        case 3:  // result, message, details
            detailsExtractor = function (args) { return args[2]; };
            break;
        default:
            throw new Error('QUnit-TAP does not support QUnit#log arguments like this.');
        }
    };

    var extractDetailsFrom = function (logArguments) {
        if (detailsExtractor) {
            return detailsExtractor(logArguments);
        }
        setupExtractor(logArguments);
        return detailsExtractor(logArguments);
    };

    tap.explain = function explain (obj) {
        if (typeof qu.jsDump !== 'undefined' && typeof qu.jsDump.parse === 'function') {
            return qu.jsDump.parse(obj);
        } else {
            return obj;
        }
    };

    tap.note = function note (obj) {
        tap.puts(escapeLineEndings('# ' + obj));
    };

    tap.diag = function diag (obj) {
        tap.note(obj);
        return false;
    };

    tap.moduleStart = function moduleStart (arg) {
        var name = (typeof arg === 'string') ? arg : arg.name;
        tap.note('module: ' + name);
    };

    tap.testStart = function testStart (arg) {
        var name = (typeof arg === 'string') ? arg : arg.name;
        tap.note('test: ' + name);
    };

    tap.log = function log () {
        var details = extractDetailsFrom(arguments),
            testLine = '';
        tap.count += 1;
        if (isFailed(details)) {
            testLine += 'not ';
        }
        testLine += ('ok ' + tap.count);
        tap.puts(formatTestLine(testLine, formatDetails(details)));
    };

    // prop in arg: failed,passed,total,runtime
    tap.done = function done (arg) {
        if (!tap.config.noPlan) {
            return;
        }
        tap.puts(tap.config.initialCount + '..' + tap.count);
    };

    var addListener = function (config) {
        // detect QUnit's multipleCallbacks feature. see jquery/qunit@34f6bc1
        var isMultipleLoggingCallbacksSupported =
                (typeof config !== 'undefined' &&
                 typeof config.log !== 'undefined' &&
                 typeof config.done !== 'undefined' &&
                 typeof config.moduleStart !== 'undefined' &&
                 typeof config.testStart !== 'undefined'),
            slice = Array.prototype.slice;
        return function (subject, observer, event) {
            var originalLoggingCallback = subject[event];
            if (isMultipleLoggingCallbacksSupported) {
                originalLoggingCallback(function () {
                    // make listener methods (moduleStart,testStart,log,done) overridable.
                    observer[event].apply(observer, slice.apply(arguments));
                });
            } else if (typeof originalLoggingCallback === 'function') {
                // do not overwrite old-style logging callbacks
                subject[event] = function () {
                    var args = slice.apply(arguments);
                    originalLoggingCallback.apply(subject, args);
                    observer[event].apply(observer, args);
                };
            }
        };
    }(qu.config);
    addListener(qu, tap, 'moduleStart');
    addListener(qu, tap, 'testStart');
    addListener(qu, tap, 'log');
    addListener(qu, tap, 'done');

    // using QUnit.tap as namespace.
    qu.tap = tap;
};

/*global exports:false*/
if (typeof exports !== 'undefined') {
    // exports qunitTap function to CommonJS world
    exports.qunitTap = qunitTap;
}
