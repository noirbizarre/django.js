describe("Django.js", function(){
    var DJANGO_INFOS = window.DJANGO_INFOS;

    it("should be defined", function(){
        expect(Django).toBeDefined();
    });

    describe('Context', function(){
        it('should have a context attribute', function(){
            expect(Django.context).toBeDefined();
        });

        it('should store STATIC_URL constant', function(){
            expect(Django.context.STATIC_URL).toBeDefined();
            expect(Django.context.STATIC_URL).toBe(DJANGO_INFOS.STATIC_URL);
        });

        it('should store MEDIA_URL constant', function(){
            expect(Django.context.MEDIA_URL).toBeDefined();
            expect(Django.context.MEDIA_URL).toBe(DJANGO_INFOS.MEDIA_URL);
        });

        it('should store available LANGUAGES', function(){
            expect(Django.context.LANGUAGES).toBeDefined();
            for (var code in DJANGO_INFOS.LANGUAGES) {
                expect(Django.context.LANGUAGES[code]).toBeDefined();
                expect(Django.context.LANGUAGES[code]).toBe(DJANGO_INFOS.LANGUAGES[code]);
            }
        });

        it('should store LANGUAGE_CODE', function(){
            expect(Django.context.LANGUAGE_CODE).toBeDefined();
            expect(Django.context.LANGUAGE_CODE).toBe(DJANGO_INFOS.LANGUAGE_CODE);
        });

        it('should store LANGUAGE_BIDI', function(){
            expect(Django.context.LANGUAGE_BIDI).toBeDefined();
            expect(Django.context.LANGUAGE_BIDI).toBe(DJANGO_INFOS.LANGUAGE_BIDI === 'True');
        });

        it('should store LANGUAGE_NAME', function(){
            expect(Django.context.LANGUAGE_NAME).toBeDefined();
            expect(Django.context.LANGUAGE_NAME).toBe(DJANGO_INFOS.LANGUAGE_NAME);
        });

        it('should store LANGUAGE_NAME_LOCAL', function(){
            expect(Django.context.LANGUAGE_NAME_LOCAL).toBeDefined();
            expect(Django.context.LANGUAGE_NAME_LOCAL).toBe(DJANGO_INFOS.LANGUAGE_NAME_LOCAL);
        });

        it('should store any custom context value', function(){
            expect(Django.context.CUSTOM).toBeDefined();
            expect(Django.context.CUSTOM).toBe('CUSTOM_VALUE');
        });
    });

    describe('Resolve reverse URLs', function(){

        it('should throw if URL name does not exists', function(){
            var notFoundUrl = function() {
                Django.url('unknown');
            };

            expect(notFoundUrl).toThrow();
        });

        describe("from arguments", function(){
            it("should resolve an URL without parameter", function(){
                expect(Django.url('test_form')).toBe('/test/form');
            });

            it("should resolve an URL with an anonymous token ", function(){
                expect(Django.url('test_arg', 41)).toBe('/test/arg/41');
            });

            it("should resolve an URL with many anonymous token", function(){
                expect(Django.url('test_arg_multi', 41, 'test')).toBe('/test/arg/41/test');
            });

            it("should resolve an URL with a named argument", function(){
                expect(Django.url('test_named', 'test')).toBe('/test/named/test');
            });

            it("should resolve an URL with many named token", function(){
                expect(Django.url('test_named_multi', 'value', 41)).toBe('/test/named/value/41');
            });

            it('should throw if number of parameters mismatch', function(){
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

        describe("from array", function(){
            it("should resolve an URL without parameter", function(){
                expect(Django.url('test_form', [])).toBe('/test/form');
            });

            it("should resolve an URL with an anonymous token ", function(){
                expect(Django.url('test_arg', [41])).toBe('/test/arg/41');
            });

            it("should resolve an URL with many anonymous token", function(){
                expect(Django.url('test_arg_multi', [41, 'test'])).toBe('/test/arg/41/test');
                expect(Django.url('test_arg_multi', ['test', 41])).toBe('/test/arg/test/41');
            });

            it("should resolve an URL with a named token", function(){
                expect(Django.url('test_named', ['test'])).toBe('/test/named/test');
            });

            it("should resolve an URL with many named token", function(){
                expect(Django.url('test_named_multi', [41, 'test'])).toBe('/test/named/41/test');
                expect(Django.url('test_named_multi', ['test', 41])).toBe('/test/named/test/41');
            });

            it('should throw if number of parameters mismatch', function(){
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

        describe("from object", function(){
            it("should resolve an URL without parameter", function(){
                expect(Django.url('test_form', {})).toBe('/test/form');
            });

            it("should resolve an URL with named parameters", function(){
                expect(Django.url('test_named', {test: 'value'})).toBe('/test/named/value');
                expect(Django.url('test_named_multi', {str: 'value', num:41})).toBe('/test/named/value/41');
            });

            it('should throw if there is an anonymous token', function(){
                var anonymous = function() {
                    Django.url('test_arg', {str: 'value'});
                };

                expect(anonymous).toThrow();
            });

            it('should throw if a token is missing', function(){
                var missing = function() {
                    Django.url('test_named_multi', {str: 'value'});
                };

                expect(missing).toThrow();
            });

            it('should not throw for unused key', function(){
                var unused = function() {
                    Django.url('test_named', {test: 'value', num:41});
                };

                expect(unused).not.toThrow();
            });
        });

    });

    describe('Resolve static', function(){
        it("should resolve a static URL", function(){
            expect(Django.file('my.json')).toBe(DJANGO_INFOS.STATIC_URL + 'my.json');
        });
    });

    describe('Internationalization', function(){

        describe("Automatically include Django provided functions", function(){
            it('gettext function should be present', function(){
                expect(gettext).toBeDefined();
            });

            it('ngettext function should be present', function(){
                expect(ngettext).toBeDefined();
            });

            it('interpolate function should be present', function(){
                expect(interpolate).toBeDefined();
            });
        });

    });

    describe('jQuery Ajax CSRF Helper', function(){

        it("should allow to post Django forms with jQuery Ajax", function(){
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

    describe('Django absolute support', function(){

        describe('when django-absolute is missing', function(){

            it("should throw calling absolute()", function(){
                var call = function() {
                    Django.absolute('test_arg', 41);
                };
                expect(call).toThrow();
            });

            it("should throw calling site()", function(){
                var call = function() {
                    Django.site('test_arg', 41);
                };
                expect(call).toThrow();
            });

        });

        describe('when django-absolute is present', function(){

            beforeEach(function() {
                Django.context.ABSOLUTE_ROOT = 'http://absolute';
                Django.context.SITE_ROOT = 'http://site';
            });

            afterEach(function() {
                delete Django.context.ABSOLUTE_ROOT;
                delete Django.context.SITE_ROOT;
            });

            it("should get absolute url", function(){
                expect(Django.absolute('test_arg', 41)).toBe('http://absolute/test/arg/41');
            });

            it("should get site url", function(){
                expect(Django.site('test_arg', 41)).toBe('http://site/test/arg/41');
            });

        });
    });

});
