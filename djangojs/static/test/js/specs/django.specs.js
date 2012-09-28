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

    describe('Reverse URL', function(){

        it("should fetch a simple URL", function(){
            expect(Django.url('django_js_json')).toBe('/urls');
        });

        it("should fetch an URL with a single parameter", function(){
            expect(Django.url('first_test', 41)).toBe('/tests/1st/41');
            expect(Django.url('second_test', 41)).toBe('/tests/2nd/41');
        });

        it("should fetch an URL with an array of parameters", function(){
            expect(Django.url('first_test', [41])).toBe('/tests/1st/41');
            expect(Django.url('second_test', [41])).toBe('/tests/2nd/41');
        });

        it("should fetch an URL with named parameters", function(){
            expect(Django.url('second_test', {test: 41})).toBe('/tests/2nd/41');
        });

        it('should throw if URL does not exists', function(){
            var notFoundUrl = function() {
                Django.url('unknown');
            };

            expect(notFoundUrl).toThrow();
        });

    });

    describe('Internationalization', function(){
        it('gettext object should be present', function(){
            expect(gettext).not.toBeUndefined();
        });
    });

});
