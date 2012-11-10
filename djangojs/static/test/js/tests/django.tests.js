var DJANGO_INFOS = window.DJANGO_INFOS;

QUnit.config.reorder = false;

module('Initialization');

test('should not be ready before init', function(){
    ok(Django);
    ok(!Django._ready);
});

asyncTest('should fire "ready" event on initialization', 1, function() {
    Django.onReady(function() {
        ok(true, '"ready" event fired');
        start();
    });

    Django.init();
});


module('Context');

test('should have a context attribute', function(){
    ok(Django.context !== undefined);
});

test('should store STATIC_URL constant', function(){
    ok(Django.context.STATIC_URL !== undefined);
    equal(Django.context.STATIC_URL, DJANGO_INFOS.STATIC_URL);
});

test('should store MEDIA_URL constant', function(){
    ok(Django.context.MEDIA_URL !== undefined);
    equal(Django.context.MEDIA_URL, DJANGO_INFOS.MEDIA_URL);
});

test('should store available LANGUAGES', function(){
    ok(Django.context.LANGUAGES !== undefined);
    for (var code in DJANGO_INFOS.LANGUAGES) {
        ok(Django.context.LANGUAGES[code] !== undefined);
        equal(Django.context.LANGUAGES[code], DJANGO_INFOS.LANGUAGES[code]);
    }
});

test('should store LANGUAGE_CODE', function(){
    ok(Django.context.LANGUAGE_CODE);
    equal(Django.context.LANGUAGE_CODE, DJANGO_INFOS.LANGUAGE_CODE);
});

test('should store LANGUAGE_BIDI', function(){
    ok(Django.context.LANGUAGE_BIDI !== undefined);
    equal(Django.context.LANGUAGE_BIDI, DJANGO_INFOS.LANGUAGE_BIDI === 'True');
});

test('should store LANGUAGE_NAME', function(){
    ok(Django.context.LANGUAGE_NAME);
    equal(Django.context.LANGUAGE_NAME, DJANGO_INFOS.LANGUAGE_NAME);
});

test('should store LANGUAGE_NAME_LOCAL', function(){
    ok(Django.context.LANGUAGE_NAME_LOCAL);
    equal(Django.context.LANGUAGE_NAME_LOCAL, DJANGO_INFOS.LANGUAGE_NAME_LOCAL);
});

test('should store any custom context value', function(){
    ok(Django.context.CUSTOM);
    equal(Django.context.CUSTOM, 'CUSTOM_VALUE');
});


module('Reverse URLs');

test('should throw if URL name does not exists', function(){
    throws(function() {
        Django.url('unknown');
    });
});

module("Reverse URLs from arguments");
test("should resolve an URL without parameter", function(){
    equal(Django.url('test_form'), '/test/form');
});

test("should resolve an URL with an anonymous token ", function(){
    equal(Django.url('test_arg', 41), '/test/arg/41');
});

test("should resolve an URL with many anonymous token", function(){
    equal(Django.url('test_arg_multi', 41, 'test'), '/test/arg/41/test');
});

test("should resolve an URL with a named argument", function(){
    equal(Django.url('test_named', 'test'), '/test/named/test');
});

test("should resolve an URL with many named token", function(){
    equal(Django.url('test_named_multi', 'value', 41), '/test/named/value/41');
});

test('should throw if number of parameters mismatch', function(){
    throws(function() {
        Django.url('test_arg', 1, 2);
    });

    throws(function() {
        Django.url('test_arg_multi', 1);
    });
});


module("Reverse URLs from array");
test("should resolve an URL without parameter", function(){
    equal(Django.url('test_form', []), '/test/form');
});

test("should resolve an URL with an anonymous token ", function(){
    equal(Django.url('test_arg', [41]), '/test/arg/41');
});

test("should resolve an URL with many anonymous token", function(){
    equal(Django.url('test_arg_multi', [41, 'test']), '/test/arg/41/test');
    equal(Django.url('test_arg_multi', ['test', 41]), '/test/arg/test/41');
});

test("should resolve an URL with a named token", function(){
    equal(Django.url('test_named', ['test']), '/test/named/test');
});

test("should resolve an URL with many named token", function(){
    equal(Django.url('test_named_multi', [41, 'test']), '/test/named/41/test');
    equal(Django.url('test_named_multi', ['test', 41]), '/test/named/test/41');
});

test('should throw if number of parameters mismatch', function(){
    throws(function() {
        Django.url('test_arg', [1, 2]);
    });

    throws(function() {
        Django.url('test_arg_multi', [1]);
    });
});


module("Reverse URLs from object");
test("should resolve an URL without parameter", function(){
    equal(Django.url('test_form', {}), '/test/form');
});

test("should resolve an URL with named parameters", function(){
    equal(Django.url('test_named', {test: 'value'}), '/test/named/value');
    equal(Django.url('test_named_multi', {str: 'value', num:41}), '/test/named/value/41');
});

test('should throw if there is an anonymous token', function(){
    throws(function() {
        Django.url('test_arg', {str: 'value'});
    });
});

test('should throw if a token is missing', function(){
    throws(function() {
        Django.url('test_named_multi', {str: 'value'});
    });
});

test('should not throw for unused key', function(){
    ok(Django.url('test_named', {test: 'value', num:41}));
});

module('Resolve static files');
test("should resolve a static URL", function(){
    equal(Django.file('my.json'), window.DJANGO_INFOS.STATIC_URL + 'my.json');
});


module('Internationalization');

test('gettext function should be present', function(){
    ok(gettext);
});

test('ngettext function should be present', function(){
    ok(ngettext);
});

test('interpolate function should be present', function(){
    ok(interpolate);
});


module('jQuery CSRF');

asyncTest("should allow to post Django forms with jQuery Ajax", 1, function(){
    var $form = $('#test-form'),
        data = {};

    $form.find("input, select").each(function(i, el) {
        data[el.name] = 'test';
    });
    $.post($form.attr('action'), data, function(response) {
        ok(true, 'form submitted');
        start();
    });
});

module('Django absolute support missing');
test('should throw on absolute() call', function(){
    throws(function() {
        Django.absolute('test_arg', 41);
    });
});

test('should throw on site() call', function(){
    throws(function() {
        Django.site('test_arg', 41);
    });
});

module('Django absolute support present', {
    setup: function() {
        Django.context.ABSOLUTE_ROOT = 'http://absolute';
        Django.context.SITE_ROOT = 'http://site';
    },
    teardown: function() {
        delete Django.context.ABSOLUTE_ROOT;
        delete Django.context.SITE_ROOT;
    }
});
test('should get an absolute url', function(){
    equal(Django.absolute('test_arg', 41), 'http://absolute/test/arg/41');
});

test('should throw a site url', function(){
    equal(Django.site('test_arg', 41), 'http://site/test/arg/41');
});
