#!/usr/bin/env node
/**
 * @file Manages translations for javascript files.
 */

var path = require('path');

var collectKey = 'collect',
    processKey = 'process',
    command = process.argv[2],
    languages = ['en', 'de', 'it', 'pl'],
    poFileTpl = path.join(__dirname, 'locale',
                          '{lang}/LC_MESSAGES/javascript.po');

if (command == collectKey) {
    var i18nExtract = require('i18n-extract'),
        jsFiles = path.join(__dirname, 'assets/js/*.js'),
        messages = i18nExtract.extractFromFiles(jsFiles, {marker: '__'});

    languages.forEach(function (lang) {
        var out = poFileTpl.replace('{lang}', lang);
        i18nExtract.mergeMessagesWithPO(messages, out, out);
    });
} else if (command == processKey) {
    var fs = require('fs'),
        conv = require('i18next-conv'),
        jsonTpl = path.join(__dirname, 'assets/i18n/{lang}/translation.json');

    var jsonDir = path.dirname(path.dirname(jsonTpl));
    if (!fs.existsSync(jsonDir)) {
        console.log('Creating missing directory: ' + jsonDir);
        fs.mkdirSync(jsonDir);
    }

    languages.forEach(function (lang) {
        conv.gettextToI18next(lang, poFileTpl.replace('{lang}', lang),
                            jsonTpl.replace('{lang}', lang), {})
    });
} else {
    /* Display help */
    var name = path.basename(process.argv[1]);
    console.log(name);
    console.log('\nManages translations for javascript files.\n');
    console.log('Usage: node ' + name + ' <command>\n');
    console.log('  ' + collectKey + '\t' +
                'Update translation files with current strings.');
    console.log('  ' + processKey + '\t' +
                'Convert translation files to json.');
    process.exit(1);
}
