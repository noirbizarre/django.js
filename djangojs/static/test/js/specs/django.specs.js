describe("Django.js", function(){

    describe('Initialization', function(){

        it("should fire 'ready' event on initilization", function(){
            var callback = jasmine.createSpy();
            $(Django).on('ready', callback);

            Django.init();

            waitsFor(function() {
                return callback.callCount > 0;
            });
            runs(function() {
                expect(callback).toHaveBeenCalled();
            });
        });

    });

    describe('Constants', function(){
        it('should store STATIC_URL constant', function(){
            expect(Django.STATIC_URL).toBeDefined();
            expect(Django.STATIC_URL).toBe(window.DJANGO_INFOS.STATIC_URL);
        });

        it('should store available LANGUAGES', function(){
            expect(Django.LANGUAGES).toBeDefined();
            expect(Django.LANGUAGES).toBe(window.DJANGO_INFOS.LANGUAGES);
        });

        it('should store LANGUAGE_CODE', function(){
            expect(Django.LANGUAGE_CODE).toBeDefined();
            expect(Django.LANGUAGE_CODE).toBe(window.DJANGO_INFOS.LANGUAGE_CODE);
        });

        it('should store LANGUAGE_BIDI', function(){
            expect(Django.LANGUAGE_BIDI).toBeDefined();
            expect(Django.LANGUAGE_BIDI).toBe(window.DJANGO_INFOS.LANGUAGE_BIDI);
        });

        it('should store LANGUAGE_NAME', function(){
            expect(Django.LANGUAGE_NAME).toBeDefined();
            expect(Django.LANGUAGE_NAME).toBe(window.DJANGO_INFOS.LANGUAGE_NAME);
        });

        it('should store LANGUAGE_NAME_LOCAL', function(){
            expect(Django.LANGUAGE_NAME_LOCAL).toBeDefined();
            expect(Django.LANGUAGE_NAME_LOCAL).toBe(window.DJANGO_INFOS.LANGUAGE_NAME_LOCAL);
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
            expect(Django.file('my.json')).toBe(window.DJANGO_INFOS.STATIC_URL + 'my.json');
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

        describe("Trans methods wraps Django provided functions", function(){
            it('should translate strings using gettext', function(){
                expect(Django.trans('Love Django.js')).toBe(gettext('Love Django.js'));
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

});
