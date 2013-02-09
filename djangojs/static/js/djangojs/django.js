(function($){

    "use strict";

    function DjangoJsError(message) {
        this.name = "DjangoJsError";
        this.message = (message || "");
    }
    DjangoJsError.prototype = new Error();
    DjangoJsError.prototype.constructor = DjangoJsError;

    var Django = window.Django = {

        urls: window.DJANGO_JS_URLS,
        context: window.DJANGO_JS_CONTEXT,
        user: window.DJANGO_JS_CONTEXT['user'],
        token_regex: /<\w*>/g,
        named_token_regex: /<(\w+)>/g,

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

        /**
         * Equivalent to ``static`` template tag.
         */
        file: function(filename) {
            return this.context.STATIC_URL + filename;
        },

        /**
         *  Fix ajax request with CSRF Django middleware.
         *  cf. https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
         */
        jquery_csrf: function() {
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
        },

        absolute: function(name, args) {
            if (!this.context.hasOwnProperty('ABSOLUTE_ROOT')) {
                throw new DjangoJsError('django-absolute needed to call absolute()');
            }
            return this.context.ABSOLUTE_ROOT + this.url(name, args);
        },

        site: function(name, args) {
            if (!this.context.hasOwnProperty('SITE_ROOT')) {
                throw new DjangoJsError('django-absolute needed to call site()');
            }
            return this.context.SITE_ROOT + this.url(name, args);
        }

    };


    /**
     * Equivalent to ``User.has_perm`` function.
     */
    Django.user.has_perm = function(permission) {
        return this.permissions.indexOf(permission) > -1;
    };

    if (window.DJANGO_JS_CRSF) {
        Django.jquery_csrf();
    }

    return Django;

}(window.jQuery));
