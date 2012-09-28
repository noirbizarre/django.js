(function(window, $, gettext){

    "use strict";

    var Django = {
        urls: {},
        token_regex: /<\w*>/g,

        /**
         * Initialize the module loading the URLs
         */
        init: function(url) {
            var that = this;
            $.getJSON(url, function(urls){
                that.urls = urls;
                $(that).trigger($.Event("ready"));
            });
        },

        /**
         * Equivalent to ``reverse`` function and ``url`` template tag.
         */
        url: function(name, args) {
            var pattern = this.urls[name] || false,
                url = pattern, key, regex, token, parts;

            if (!url) {
                throw('URL for view "' + name + '" not found');
            }

            if ($.isPlainObject(args)) {
                for (key in args) {
                    token = '<' + key + '>';
                    if (!url.match(token)) {
                        throw('Key "' + key + '" not found in pattern "' + pattern +'"');
                    }
                    url = url.replace(token, args[key]);
                }
            } else if ($.isArray(args)) {
                if (url.match(this.token_regex).length != args.length) {
                    throw('Wrong number of argument for url "' + name + '"');
                }
                parts = url.split(this.token_regex);
                url = parts[0];
                for (key=0; key < args.length; key++) {
                    url += args[key] + parts[key + 1];
                }
            } else {
                url = url.replace(this.token_regex, args);
            }
            return url;
        },

        /**
         * Equivalent to trans template tag
         */
        trans: function(string) {
            return gettext(string);
        }
    };

    window.Django = Django;

    // Fix ajax request with CSRF Django middleware
    // cf. https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
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

}(window, window.jQuery, window.gettext));
