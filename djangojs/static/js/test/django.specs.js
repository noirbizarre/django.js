/**
 * Django.js test suite
 *
 * It depends on djangojs.test_urls
 */
describe("Django.js", function() {
    var DJANGO_INFOS = window.DJANGO_INFOS;

    it("is defined", function() {
        expect(Django).toBeDefined();
    });

    describe('Initialization', function() {
        var backup_context, backup_urls;

        beforeEach(function() {
            backup_context = window.DJANGO_JS_CONTEXT;
            backup_urls = window.DJANGO_JS_URLS;
        });

        afterEach(function() {
            window.DJANGO_JS_CONTEXT = backup_context;
            window.DJANGO_JS_URLS = backup_urls;
            Django.initialize();
        });

        it('can be initialized without parameter from global vars content', function() {
            Django.initialize();
            expect(Django.context).toEqual(window.DJANGO_JS_CONTEXT);
            expect(Django.urls).toEqual(window.DJANGO_JS_URLS);
        });

        describe('can be initialized with an optionnal object parameter', function() {
            it('with an "urls" attribute containing json', function() {
                var urls = {'my-url': '/my-url'};

                Django.initialize({urls: urls});

                expect(Django.urls).toEqual(urls);
                expect(Django.context).toEqual(window.DJANGO_JS_CONTEXT);
            });

            it('with a "context" attribute containing json', function() {
                var context = {'fake': true};

                Django.initialize({context: context});

                expect(Django.context).toEqual(context);
                expect(Django.urls).toEqual(window.DJANGO_JS_URLS);
            });

            it('with an "urls" attribute containing a remote url', function() {
                var urls = {'my-url': '/my-url'};
                spyOn($, "ajax").andCallFake(function(params) {
                    expect(params.url).toEqual('http://somewhere');
                    params.success(urls);
                });

                Django.initialize({urls: 'http://somewhere'});

                expect(Django.urls).toEqual(urls);
                expect(Django.context).toEqual(window.DJANGO_JS_CONTEXT);
            });

            it('with a "context" attribute containing a remote url', function() {
                var context = {'fake': true};
                spyOn($, "ajax").andCallFake(function(params) {
                    expect(params.url).toEqual('http://somewhere');
                    params.success(context);
                });

                Django.initialize({context: 'http://somewhere'});

                expect(Django.context).toEqual(context);
                expect(Django.urls).toEqual(window.DJANGO_JS_URLS);
            });

            it('with any combination of both json and a remote url', function() {
                var urls = {'my-url': '/my-url'},
                    context = {'fake': true};

                spyOn($, "ajax").andCallFake(function(params) {
                    expect(params.url).toEqual('http://somewhere');
                    params.success(urls);
                });

                Django.initialize({urls: 'http://somewhere', context: context});

                expect(Django.urls).toEqual(urls);
                expect(Django.context).toEqual(context);
            });

        });

    })

    describe('Context', function() {
        it('have a context attribute', function() {
            expect(Django.context).toBeDefined();
        });

        it('store STATIC_URL constant', function() {
            expect(Django.context.STATIC_URL).toBeDefined();
            expect(Django.context.STATIC_URL).toBe(DJANGO_INFOS.STATIC_URL);
        });

        it('store MEDIA_URL constant', function() {
            expect(Django.context.MEDIA_URL).toBeDefined();
            expect(Django.context.MEDIA_URL).toBe(DJANGO_INFOS.MEDIA_URL);
        });

        it('store available LANGUAGES', function() {
            expect(Django.context.LANGUAGES).toBeDefined();
            for (var code in DJANGO_INFOS.LANGUAGES) {
                expect(Django.context.LANGUAGES[code]).toBeDefined();
                expect(Django.context.LANGUAGES[code]).toBe(DJANGO_INFOS.LANGUAGES[code]);
            }
        });

        it('store LANGUAGE_CODE', function() {
            expect(Django.context.LANGUAGE_CODE).toBeDefined();
            expect(Django.context.LANGUAGE_CODE).toBe(DJANGO_INFOS.LANGUAGE_CODE);
        });

        it('store LANGUAGE_BIDI', function() {
            expect(Django.context.LANGUAGE_BIDI).toBeDefined();
            expect(Django.context.LANGUAGE_BIDI).toBe(DJANGO_INFOS.LANGUAGE_BIDI === 'True');
        });

        it('store LANGUAGE_NAME', function() {
            expect(Django.context.LANGUAGE_NAME).toBeDefined();
            expect(Django.context.LANGUAGE_NAME).toBe(DJANGO_INFOS.LANGUAGE_NAME);
        });

        it('store LANGUAGE_NAME_LOCAL', function() {
            expect(Django.context.LANGUAGE_NAME_LOCAL).toBeDefined();
            expect(Django.context.LANGUAGE_NAME_LOCAL).toBe(DJANGO_INFOS.LANGUAGE_NAME_LOCAL);
        });

        it('store any custom context value', function() {
            expect(Django.context.CUSTOM).toBeDefined();
            expect(Django.context.CUSTOM).toBe('CUSTOM_VALUE');
        });

        it('store the user and its basic attributes', function() {
            expect(Django.context.user).toBeDefined();
            expect(Django.context.user.username).toBeDefined();
            expect(Django.context.user.is_authenticated).toBeDefined();
            expect(Django.context.user.is_staff).toBeDefined();
            expect(Django.context.user.is_superuser).toBeDefined();
            expect(Django.context.user.permissions).toBeDefined();
        });

    });

    describe('Resolve reverse URLs', function() {

        it('throw if URL name does not exists', function() {
            var notFoundUrl = function() {
                Django.url('unknown');
            };

            expect(notFoundUrl).toThrow();
        });

        describe("from arguments", function() {
            it("resolve an URL without parameter", function() {
                expect(Django.url('test_form')).toBe('/test/form');
            });

            it("resolve an URL with an anonymous token ", function() {
                expect(Django.url('test_arg', 41)).toBe('/test/arg/41');
            });

            it("resolve an URL with many anonymous token", function() {
                expect(Django.url('test_arg_multi', 41, 'test')).toBe('/test/arg/41/test');
            });

            it("resolve an URL with a named argument", function() {
                expect(Django.url('test_named', 'test')).toBe('/test/named/test');
            });

            it("resolve an URL with many named token", function() {
                expect(Django.url('test_named_multi', 'value', 41)).toBe('/test/named/value/41');
            });

            it("resolve an URL with an anonymous token and 0 as value", function() {
                expect(Django.url('test_arg', 0)).toBe('/test/arg/0');
            });

            it('throw if number of parameters mismatch', function() {
                var tooMany = function() {
                    Django.url('test_arg', 1, 2);
                };

                var notEnough = function() {
                    Django.url('test_arg_multi', 1);
                };

                expect(notEnough).toThrow();
                expect(tooMany).toThrow();
            });

        });

        describe("from array", function() {
            it("resolve an URL without parameter", function() {
                expect(Django.url('test_form', [])).toBe('/test/form');
            });

            it("resolve an URL with an anonymous token ", function() {
                expect(Django.url('test_arg', [41])).toBe('/test/arg/41');
            });

            it("resolve an URL with many anonymous token", function() {
                expect(Django.url('test_arg_multi', [41, 'test'])).toBe('/test/arg/41/test');
                expect(Django.url('test_arg_multi', ['test', 41])).toBe('/test/arg/test/41');
            });

            it("resolve an URL with a named token", function() {
                expect(Django.url('test_named', ['test'])).toBe('/test/named/test');
            });

            it("resolve an URL with many named token", function() {
                expect(Django.url('test_named_multi', [41, 'test'])).toBe('/test/named/41/test');
                expect(Django.url('test_named_multi', ['test', 41])).toBe('/test/named/test/41');
            });

            it("resolve an URL with an anonymous token and 0 as value", function() {
                expect(Django.url('test_arg', [0])).toBe('/test/arg/0');
            });

            it('throw if number of parameters mismatch', function() {
                var tooMany = function() {
                    Django.url('test_arg', [1, 2]);
                };

                var notEnough = function() {
                    Django.url('test_arg_multi', [1]);
                };

                expect(notEnough).toThrow();
                expect(tooMany).toThrow();
            });

        });

        describe("from object", function() {
            it("resolve an URL without parameter", function() {
                expect(Django.url('test_form', {})).toBe('/test/form');
            });

            it("resolve an URL with named parameters", function() {
                expect(Django.url('test_named', {
                    test: 'value'
                })).toBe('/test/named/value');
                expect(Django.url('test_named_multi', {
                    str: 'value',
                    num: 41
                })).toBe('/test/named/value/41');
            });

            it("resolve an URL with named parameters and 0 as value", function() {
                expect(Django.url('test_named', {
                    test: 0
                })).toBe('/test/named/0');
                expect(Django.url('test_named_multi', {
                    str: 'value',
                    num: 0
                })).toBe('/test/named/value/0');
            });

            it('throw if there is an anonymous token', function() {
                var anonymous = function() {
                    Django.url('test_arg', {
                        str: 'value'
                    });
                };

                expect(anonymous).toThrow();
            });

            it('throw if a token is missing', function() {
                var missing = function() {
                    Django.url('test_named_multi', {
                        str: 'value'
                    });
                };

                expect(missing).toThrow();
            });

            it("don't throw for unused key", function() {
                var unused = function() {
                    Django.url('test_named', {
                        test: 'value',
                        num: 41
                    });
                };

                expect(unused).not.toThrow();
            });
        });

        describe('with namespace', function() {

            it("resolve an URL with a namespace", function() {

                expect(Django.url('ns1:fake')).toBe('/test/namespace1/fake');

            });

            it("not resolve a namespaced url without namespace", function() {
                var namespaceless = function() {
                    Django.url('fake');
                };
                expect(namespaceless).toThrow();
            });

            it("resolve an URL with a nested namespace", function() {
                var notLeaf = function() {
                    Django.url('ns2:nested');
                };

                var notNested = function() {
                    Django.url('ns2:fake');
                };

                expect(Django.url('ns2:nested:fake')).toBe('/test/namespace2/nested/fake');
                expect(notLeaf).toThrow();
                expect(notNested).toThrow();
            });

            it("resolve an URL with an instance namespace", function() {
                expect(Django.url('app1:fake')).toBe('/test/namespace1/fake');
            });

            it("resolve an URL with a nested instance namespace", function() {
                expect(Django.url('app2:nested:fake')).toBe('/test/namespace2/nested/fake');
                expect(Django.url('ns2:appnested:fake')).toBe('/test/namespace2/nested/fake');
                expect(Django.url('app2:appnested:fake')).toBe('/test/namespace2/nested/fake');
            });
        });

    });

    describe('Resolve static', function() {
        it("resolve a static URL", function() {
            expect(Django.file('my.json')).toBe(DJANGO_INFOS.STATIC_URL + 'my.json');
            expect(Django.static('my.json')).toBe(DJANGO_INFOS.STATIC_URL + 'my.json');
        });
    });

    describe('Internationalization', function() {

        describe("Automatically include Django provided functions", function() {
            it('loads the "gettext" function', function() {
                expect(gettext).toBeDefined();
            });

            it('loads the "ngettext" function', function() {
                expect(ngettext).toBeDefined();
            });

            it('loads the "interpolate" function', function() {
                expect(interpolate).toBeDefined();
            });
        });

    });

    describe('User object', function() {

        it('allow access to the basic user attributes', function() {
            expect(Django.user).toBeDefined();
            expect(Django.user.username).toBeDefined();
            expect(Django.user.is_authenticated).toBeDefined();
            expect(Django.user.is_staff).toBeDefined();
            expect(Django.user.is_superuser).toBeDefined();
        });

        describe('Permissions handling', function() {
            it('expose a permission array and a permission checker helper', function() {
                expect(Django.user.permissions).toEqual(jasmine.any(Array));
                expect(Django.user.has_perm).toEqual(jasmine.any(Function));
            });

            it('give permission if present in permissions', function() {
                Django.context.user.permissions.push('fake.something');
                expect(Django.user.has_perm('fake.something')).toBeTruthy();
            });

            it('deny permission if not present in permissions', function() {
                expect(Django.user.has_perm('fake.something_else')).toBeFalsy();
            });
        });

        describe('When settings.JS_USER_ENABLED=False', function() {
            var user_backup;

            beforeEach(function() {
                user_backup = window.DJANGO_JS_CONTEXT['user'];
                delete window.DJANGO_JS_CONTEXT['user'];
                Django.initialize();
            });

            afterEach(function() {
                window.DJANGO_JS_CONTEXT['user'] = user_backup;
                Django.initialize();
            });

            it('should not expose user', function() {
                expect(Django.user).toBeUndefined();
            });
        });
    });


    describe('The CSRF Token', function() {
        beforeEach(function() {
            this.csrfToken = $('#csrf-token').text();
        });

        it("is accessible through csrf_token()", function() {
            var c = Django.csrf_token();
            expect(c).toBe(this.csrfToken);
        });

        it("Template Tag can be replicated with csrf_element()", function() {
            var $csrfTag = $('#test-csrf-elem input[name="csrfmiddlewaretoken"]');
            var e = Django.csrf_element();
            expect(e).toBe($csrfTag[0].outerHTML);
        });
    });

    describe('jQuery Ajax CSRF Helper', function() {

        it("allow to post Django forms with jQuery Ajax", function() {
            var callback = jasmine.createSpy(),
                $form = $('#test-form'),
                data = {};

            $form.find("input, select").each(function(i, el) {
                data[el.name] = 'test';
            });
            $.post($form.attr('action'), data, callback);

            waitsFor(function() {
                return callback.callCount > 0;
            });
            runs(function() {
                expect(callback).toHaveBeenCalled();
            });
        });

    });

    describe('Asynchronous and reloading support', function() {

        afterEach(function() {
            Django.initialize();
        });

        it('provide context and user reloading', function() {
            spyOn($, "ajax").andCallFake(function(params) {
                expect(params.url).toEqual(Django.url('django_js_context'));

                params.success({
                    "fake": true,
                    "user": {
                        "username": "fake",
                        "is_authenticated": false,
                        "permissions": [],
                        "is_staff": false,
                        "is_superuser": false
                    }
                });
            });

            var callback = jasmine.createSpy();

            Django.reload(callback);

            expect(callback).toHaveBeenCalled();
            expect(Django.context.fake).toBeTruthy();
            expect(Django.user.username).toEqual('fake');
            expect(Django.user.has_perm).toBeDefined();
        });

    });

    describe('Django absolute support', function() {

        describe('when django-absolute is missing', function() {

            it("throw calling absolute()", function() {
                var call = function() {
                    Django.absolute('test_arg', 41);
                };
                expect(call).toThrow();
            });

            it("throw calling site()", function() {
                var call = function() {
                    Django.site('test_arg', 41);
                };
                expect(call).toThrow();
            });

        });

        describe('when django-absolute is present', function() {

            beforeEach(function() {
                Django.context.ABSOLUTE_ROOT = 'http://absolute';
                Django.context.SITE_ROOT = 'http://site';
            });

            afterEach(function() {
                delete Django.context.ABSOLUTE_ROOT;
                delete Django.context.SITE_ROOT;
            });

            it("resolve absolute url", function() {
                expect(Django.absolute('test_arg', 41)).toBe('http://absolute/test/arg/41');
            });

            it("resolve site url", function() {
                expect(Django.site('test_arg', 41)).toBe('http://site/test/arg/41');
            });

        });
    });

});
