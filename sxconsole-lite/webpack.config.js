var glob = require('glob'),
    path = require('path'),
    fs = require('fs');

var webpack = require('webpack'),
    ExtractTextPlugin = require('extract-text-webpack-plugin'),
    yaml = require('js-yaml'),
    mergeDirs = require('merge-dirs');


/* Load and process the conf */
try {
    var conf = yaml.safeLoad(fs.readFileSync('./conf.yaml'));
}
catch (e) {
    var conf = {};
}

if (conf.server) {
    var debug = conf.server.debug;
} else {
    var debug = false;
}


var skin_name = conf.skin || 'default';

/** Copy over the skin's images */
var skinImgPath = path.join('skins', skin_name, 'img');
if (fs.existsSync(skinImgPath)) {
    mergeDirs(skinImgPath, 'assets/img', /* overwriteExistingFiles= */ true);
}

/** Load and process skin conf */
try {
    var skin = yaml.safeLoad(fs.readFileSync(
        path.join('skins', skin_name, 'skin.yaml')));
}
catch (e) {
    console.error('Skin missing or is not a yaml file:', skin_name);
    var skin = {};
}

var customization = JSON.stringify(skin.sass || {});


module.exports = {
    context: __dirname + '/assets',

    entry: {
        /* Page-related js is added dynamically below */
        i18n: ['./i18n'],
        vendor: [
            './scss/styles.scss',
            'bootstrap',
            'browser-cookies',
            'bytes',
            'c3',
            'i18next/lib/i18next.js',
            'jquery',
            'lodash',
            'moment',
            'perfect-scrollbar/jquery',
            'react',
            'react-dom',
        ],
    },
    output: {
        path: __dirname + '/assets/build/',
        filename: '[name].js'
    },
    plugins: [
        new webpack.DefinePlugin({
            "process.env.NODE_ENV":
                (debug) ? '"dev"' : '"production"',
        }),
        new webpack.ProvidePlugin({
            '$': 'jquery',
            '_': 'lodash',
            '__': __dirname + '/assets/i18n',
            'jQuery': 'jquery', /* for bootstrap */
            'window.jQuery': 'jquery', /* for highstock */
        }),
        new webpack.optimize.CommonsChunkPlugin({
            names: ['i18n', 'vendor']
        }),
        new ExtractTextPlugin('styles.css')
    ],
    module: {
        loaders: [
            { test: /\.js$/, exclude: /node_modules/, loader: 'babel-loader' },
            { test: /\.scss$/, loader: ExtractTextPlugin.extract(
                'style-loader', 'css!sass!jsontosass?' + customization) }
        ]
    }
};

glob.sync(__dirname + '/assets/js/*.js').forEach(function (filePath) {
    var id = path.basename(filePath).split('.')[0];
    module.exports.entry[id] = filePath;
});
