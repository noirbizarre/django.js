describe("Django.js", function(){

    it("should fire 'ready' event on initilization", function(){
        var callback = jasmine.createSpy();
        $(Django).on('ready', callback);
        waitsFor(function() {
            return callback.callCount > 0;
        });
        runs(function() {
            expect(callback).toHaveBeenCalled();
        });
    });

    it("should fetch a simple URL", function(){
        expect(Django.url('django_js_json')).toBe('/urls');
    });

    it("should fetch an URL with a single parameter", function(){
        expect(Django.url('first_test', 41)).toBe('/1st/41');
        expect(Django.url('second_test', 41)).toBe('/2nd/41');
    });

    it("should fetch an URL with an array of parameters", function(){
        expect(Django.url('first_test', [41])).toBe('/1st/41');
        expect(Django.url('second_test', [41])).toBe('/2nd/41');
    });

    it("should fetch an URL with named parameters", function(){
        expect(Django.url('second_test', {test: 41})).toBe('/2nd/41');
    });


});
