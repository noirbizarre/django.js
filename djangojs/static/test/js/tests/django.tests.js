var DJANGO_INFOS = window.DJANGO_INFOS;

QUnit.config.reorder = false;

module('Initialization');

asyncTest('should fire "ready" event on initilization', 1, function() {
    $(Django).on('ready', function() {
        ok(true, '"ready" event fired');
        start();
    });

    Django.init();
});


module('Constants');

test('should store STATIC_URL constant', function(){
    ok(Django.STATIC_URL !== undefined);
    equal(Django.STATIC_URL, DJANGO_INFOS.STATIC_URL);
});

test('should store available LANGUAGES', function(){
    ok(Django.LANGUAGES !== undefined);
    equal(Django.LANGUAGES, DJANGO_INFOS.LANGUAGES);
});

test('should store LANGUAGE_CODE', function(){
    ok(Django.LANGUAGE_CODE);
    equal(Django.LANGUAGE_CODE, DJANGO_INFOS.LANGUAGE_CODE);
});

test('should store LANGUAGE_BIDI', function(){
    ok(Django.LANGUAGE_BIDI);
    equal(Django.LANGUAGE_BIDI, DJANGO_INFOS.LANGUAGE_BIDI);
});

test('should store LANGUAGE_NAME', function(){
    ok(Django.LANGUAGE_NAME);
    equal(Django.LANGUAGE_NAME, DJANGO_INFOS.LANGUAGE_NAME);
});

test('should store LANGUAGE_NAME_LOCAL', function(){
    ok(Django.LANGUAGE_NAME_LOCAL);
    equal(Django.LANGUAGE_NAME_LOCAL, DJANGO_INFOS.LANGUAGE_NAME_LOCAL);
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


module("Trans method");

test('should translate strings using gettext', function(){
    equal(Django.trans('Love Django.js'), gettext('Love Django.js'));
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
