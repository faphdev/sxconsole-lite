let $tabs = $('#cluster-tabs a[data-toggle=tab]');

/* Load last used tab */
let lastTab = window.localStorage.ClusterTabs || $tabs.attr('href');
$tabs.filter('[href="' + lastTab + '"]').tab('show');

/* Save last used tab */
$tabs.on('show.bs.tab', function (e) {
    window.localStorage.ClusterTabs = $(e.target).attr('href');
});
