(function(window, $){

    "use strict";

    function DjangoJsError(message) {
        this.name = "DjangoJsError";
        this.message = (message || "");
    }
    DjangoJsError.prototype = new Error();
    DjangoJsError.prototype.constructor = DjangoJsError;

    var Django = window.Django = {

        urls: undefined,
        context: undefined,
        token_regex: /<\w*>/g,
        named_token_regex: /<(\w+)>/g,

        _ready: false,


        /**
         * Initialize the module loading the URLs
         */
        init: function() {
            this._jquery_csrf();

            $.getJSON(window.DJANGO_JS['URLS_JSON'], function(urls){
                Django.urls = urls;
                Django._check_ready();
            }).error(function() {
                throw new DjangoJsError("Unable to fetch urls JSON file");
            });

            $.getJSON(window.DJANGO_JS['CONTEXT_JSON'], function(context){
                Django.context = context;
                Django._check_ready();
            }).error(function() {
                throw new DjangoJsError("Unable to fetch context JSON file");
            });
        },

        /**
         * Execute callback when urls and context are ready.
         */
        onReady: function(callback) {
            if (this._ready) {
                callback();
            } else {
                $(this).one('ready', callback);
            }
        },

        _check_ready: function() {
            if (this.urls && this.context) {
                this._ready = true;
                $(this).trigger($.Event("ready"));
            }
        },

        /**
         * Equivalent to ``reverse`` function and ``url`` template tag.
         */
        url: function(name, args) {
            var pattern = this.urls[name] || false,
                url = pattern,
                key, regex, token, parts;

            if (!url) {
                throw new DjangoJsError('URL for view "' + name + '" not found');
            }

            if (!args) {
                return url;
            }

            if ($.isArray(args)) {
                return this._url_from_array(name, pattern, args);
            }
            else if ($.isPlainObject(args)) {
                return this._url_from_object(name, pattern, args);
            }
            else {
                var argsArray = Array.prototype.slice.apply(arguments, [1, arguments.length]);
                return this._url_from_array(name, pattern, argsArray);
            }
            return url;
        },

        _url_from_array: function(name, pattern, array) {
            var matches = pattern.match(this.token_regex),
                parts = pattern.split(this.token_regex),
                url = parts[0];

            if (!matches && array.length === 0) {
                return url;
            }

            if (matches && matches.length != array.length) {
                throw new DjangoJsError('Wrong number of argument for pattern "' + name + '"');
            }


            for (var idx=0; idx < array.length; idx++) {
                url += array[idx] + parts[idx + 1];
            }

            return url;
        },

        _url_from_object: function(name, pattern, object) {
            var url = pattern,
                tokens = pattern.match(this.token_regex);

            if (!tokens) {
                return url;
            }

            for (var idx=0; idx < tokens.length; idx++) {
                var token = tokens[idx],
                    prop = token.slice(1, -1),
                    value = object[prop];

                if (!value) {
                    throw new DjangoJsError('Property "' + prop + '" not found');
                }

                url = url.replace(token, value);
            }

            return url;
        },

        file: function(filename) {
            return this.context.STATIC_URL + filename;
        },

        /**
         * Equivalent to trans template tag
         */
        trans: function(string) {
            return window.gettext(string);
        },

        /**
         *  Fix ajax request with CSRF Django middleware.
         *  cf. https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
         */
        _jquery_csrf: function() {
            $(document).ajaxSend(function(event, xhr, settings) {
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = $.trim(cookies[i]);
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }

                function sameOrigin(url) {
                    // url could be relative or scheme relative or absolute
                    var host = document.location.host; // host + port
                    var protocol = document.location.protocol;
                    var sr_origin = '//' + host;
                    var origin = protocol + sr_origin;
                    // Allow absolute or scheme relative URLs to same origin
                    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') || (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                    // or any other URL that isn't scheme relative or absolute i.e relative.
                    !(/^(\/\/|http:|https:).*/.test(url));
                }

                function safeMethod(method) {
                    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
                }

                if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            });
        }

    };

}(window, window.jQuery));
