var c3 = require('c3');
var bytes = require('bytes');
var moment = require('moment');

var $stats = $('#stats');
var statsUrl = $stats.data('url');

$.getJSON($stats.data('init-url'), initStats);


var stamp;
function initStats (data) {
    stamp = new Date().getTime();

    $stats.html('');
    addChart(data, 'space_usage', __("Used space"));
}

var _charts = {};

/** @function updates graphs with new data for given time range */
var updateGraphs = function (range) {
    /** Keep all charts in sync */
    _.each(_charts, function (chart, id) {
        var url = [
                statsUrl,
                '?stat=' + id,
                '&from=' + Math.round(range[0] / 1000),
                '&till=' + Math.round(range[1] / 1000)].join('');
        $.getJSON(url, onLoad);

        function onLoad (data) {
            var columns = data.stats,
                timeline = columns[0];

            chart.load({
                columns: columns,
                done: function () {
                    // Zoom in to the new data (timeline[0] is 'x')
                    chart.zoom([timeline[1], _.last(timeline)]);
                }
            });
        }
    });

};


var $controls = $('#stats-controls');

$controls.find('.js-intervals button').on('click', function () {
    /** Calculate the delta (e.g. '24 30' = 1 month) */
    var delta = this.dataset.delta
            .split(' ')
            .map(n => parseInt(n))
            .reduce((l, r) => l * r)
            * 1000 * 60 * 60;

    /** Zoom and load data */
    updateGraphs([stamp - delta, stamp]);
})

/** @function - mount and create a new chart */
function addChart (data, id, label) {
    var stats = data[id],
        $elem = $('<div />').appendTo($stats);
    $elem.before($('<h4 />', {text: label}));

    var options = {
            bindto: $elem[0],
            data: {
                columns: stats,
            },
            zoom: {
                onzoomend: _.debounce(updateGraphs, 100)
            },
        };

    var chart = makeChart(options);
    chart.label = label;

    _charts[id] = chart;
}


function makeChart () {
    var defaultOptions = {
            transition: {
                duration: 0,
            },
            data: {
                type: 'area',
                x: 'x',
            },
            axis: {
                x: {
                    type: 'timeseries',
                    tick: {
                        count: 15,
                        multiline: true,
                        format: function (d) {
                            var z = this.api.zoom(),
                                delta = z[1].getTime() - z[0].getTime(),
                                d = moment(d),
                                day = 1000 * 60 * 60 * 24,
                                week = day * 7,
                                year = day * 365
                            if (delta < day)
                                return d.format('HH:mm')
                            else if (delta < year)
                                return d.format('D MMM')
                            else
                                return d.format('MM.YYYY')

                        }
                    }
                },
                y: {
                    tick: {
                        format: bytes,
                    }
                }
            },
            tooltip: {
                format: {
                    title: function (d) {
                        return moment(d).format('YYYY-MM-DD HH:mm');
                    }
                }
            },
            point: {
                show: false,
            },
            zoom: {
                enabled: true,
                extent: [1, 30 * 24 * 2],
            }
        };
    var options = _.merge(defaultOptions, ..._.toArray(arguments)),
        chart = c3.generate(options);

    /** Stack all chart series */
    chart.groups([_.map(chart.data(), 'id')]);

    /** Expand chart range for dragging and zoom back to the original range */
    var timeline = options.data.columns[0],
        min = timeline[1],
        max = timeline[timeline.length - 1];
    refreshRange(chart, stamp);
    chart.zoom([min, max]);

    return chart;
}

function refreshRange (chart, stamp) {
    chart.axis.range({
        min: {x: stamp - 1000 * 60 * 60 * 24 * 30},
        max: {x: stamp},
    });
}

function refresh () {
    stamp = new Date().getTime();

    var delta;
    _.each(_charts, function (chart, id) {
        if (!delta) {
            var zoom = chart.zoom();
            delta = zoom[1].getTime() - zoom[0].getTime();
        }
        refreshRange(chart, stamp);
    });

    updateGraphs([stamp - delta, stamp]);
}
$('.js-refresh').on('click', _.debounce(refresh, 100));


var autoRefreshID;
$('.js-auto-refresh').on('click', function () {
    var $this = $(this),
        on = 'btn-success',
        off = 'btn-default';
    if ($this.hasClass(on)) {
        clearInterval(autoRefreshID);
    } else {
        autoRefreshID = setInterval(refresh, 5000);
    }
    $this.toggleClass(off).toggleClass(on);
}).click();  // Enable by default
