describe("Django.js", function(){

    var django_js_json = '/urls';

    describe('Initialization', function(){

        it("should fire 'ready' event on initilization", function(){
            var callback = jasmine.createSpy();
            $(Django).on('ready', callback);

            Django.init(django_js_json);

            waitsFor(function() {
                return callback.callCount > 0;
            });
            runs(function() {
                expect(callback).toHaveBeenCalled();
            });
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
                expect(Django.url('django_js_json')).toBe('/urls');
            });

            it("should resolve an URL with an anonymous token ", function(){
                expect(Django.url('test_arg', 41)).toBe('/tests/arg/41');
            });

            it("should resolve an URL with many anonymous token", function(){
                expect(Django.url('test_arg_multi', 41, 'test')).toBe('/tests/arg/41/test');
            });

            it("should resolve an URL with a named argument", function(){
                expect(Django.url('test_named', 'test')).toBe('/tests/named/test');
            });

            it("should resolve an URL with many named token", function(){
                expect(Django.url('test_named_multi', 'value', 41)).toBe('/tests/named/value/41');
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
                expect(Django.url('django_js_json'), []).toBe('/urls');
            });

            it("should resolve an URL with an anonymous token ", function(){
                expect(Django.url('test_arg', [41])).toBe('/tests/arg/41');
            });

            it("should resolve an URL with many anonymous token", function(){
                expect(Django.url('test_arg_multi', [41, 'test'])).toBe('/tests/arg/41/test');
                expect(Django.url('test_arg_multi', ['test', 41])).toBe('/tests/arg/test/41');
            });

            it("should resolve an URL with a named argument", function(){
                expect(Django.url('test_named', ['test'])).toBe('/tests/named/test');
            });

            it("should resolve an URL with many named token", function(){
                expect(Django.url('test_named_multi', [41, 'test'])).toBe('/tests/named/41/test');
                expect(Django.url('test_named_multi', ['test', 41])).toBe('/tests/named/test/41');
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
                expect(Django.url('django_js_json'), {}).toBe('/urls');
            });

            it("should resolve an URL with named parameters", function(){
                expect(Django.url('test_named', {test: 'value'})).toBe('/tests/named/value');
                expect(Django.url('test_named_multi', {str: 'value', num:41})).toBe('/tests/named/value/41');
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

    describe('Internationalization', function(){
        it('gettext object should be present', function(){
            expect(gettext).not.toBeUndefined();
        });
    });

    describe('jQuery Ajax CRSF Fix', function(){

    });

});
