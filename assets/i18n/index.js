let moment = require('moment');
let i18n = require('i18next/lib/i18next.js'),
    translations = require('i18next-resource-store-loader!.');

let language = document.documentElement.getAttribute('lang');

moment.locale(language);

// Remove falsy entries from translations[lang].translation dictionaries
translations = _.mapValues(translations, function (lang) {
    lang.translation = _.pickBy(lang.translation)
    return lang;
});

i18n.init({
    load: 'currentOnly',
    resources: translations,
    lng: language,
    // These values can be literally anything, as long as it won't appear in
    // our messages...
    keySeparator: '\t.\t',
    nsSeparator: '\t:\t',
});

module.exports = i18n.t.bind(i18n);
