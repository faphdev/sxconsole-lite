let moment = require('moment');
let i18n = require('i18next/lib/i18next.js'),
    translations = require('i18next-resource-store-loader!.');

let language = document.documentElement.getAttribute('lang');

moment.locale(language);

i18n.init({
    load: 'currentOnly',
    resources: translations,
    lng: language,
    // No namespaces and keys
    nsSeparator: false,
    keySeparator: false,
    // We expect only non-empty strings:
    returnNull: false,
    returnEmptyString: false,
    returnObjects: false,
});

module.exports = i18n.t.bind(i18n);
