/** @file Provides global functionalities */

/** Add a scrollbar to sidebar cluster list */
(function () {
    var unit = 15,
        $panel = $('.js-side-panel'),
        $list = $('.js-cluster-list');

    if ($panel.length && $list.length) {
        require('perfect-scrollbar/jquery')($);  // Initialize $.perfectScrollbar
        $list.perfectScrollbar({
            suppressScrollX: true,
        });

        /* Update the scrollbar and cluster list on window resize */
        $(window).on('resize', _.debounce(function () {
            if ($panel.css('position') == 'fixed') {
                $list.height($panel.height() - $list.position().top - unit);
            } else {
                $list.height(''); // Mobile view - restore height
            }
            $list.perfectScrollbar('update');
        }, 100)).resize();
    }
})();


/** Focus the first visible form input on the page.
 * Super useful on login forms, etc. */
(function () {
    $('form:not(.js-noautofocus) input:not([type="hidden"])').first().focus();
})();


/** Truncate potentially long strings and add tooltips with original text */
(function () {
    $.fn.trunc = function () {

        this.find('.js-trunc').each(function () {
            var $this = $(this),
                $parent = $this.parent();

            $parent.css('white-space', 'nowrap');

            /* Load and save original text */
            var text = $this.data('original-text');
            if (!text) {
                text = $this.text();
                $this.data('original-text', text);
            } else {
                $this.text(text);
            }

            var targetWidth = $parent.width() -
                    ($this.position().left + Math.max(0, $parent.position().left)),
                ellipsis = "\u2026",
                left = text.substr(0, text.length/2).split(''),
                right = text.substr(text.length/2).split(''),
                i = 0,
                finished = function () {
                    if ($this.width() <= targetWidth) {
                        return true;
                    }
                    $this.text([left.join(''), right.join('')].join(ellipsis));
                    return (_.some([left, right], _.isEmpty))
                };

            /* Remove letters from the middle until text is short enough */
            while (!finished()) {
                (i++ % 2) ? left.pop() : right.shift()
            }

            /* Add a tooltip with the original text */
            if ($this.text() !== text) {
                $this.attr('title', text);
            } else {
                $this.attr('title', null);
            }

        });
    };

    var $body = $('body'),
        reTrunc = function () {
            $body.trunc();
        };

    // Apply truncation on $(document).ready
    $(setTimeout(reTrunc, 1));

    $(window).on('resize', _.debounce(function () {
        reTrunc();
    }, 100));

    $body.on('shown.bs.tab', function (e) {
        var query = $(e.target).attr('href');
        $(query).trunc();
    });
})();


/** Language selector */
(function () {
    var $form = $('.js-language-select');
    $form.on('click', 'a', function () {
        $form.find('input[name=language]').val(this.dataset.lang);
        $form.submit();
    });
})()
