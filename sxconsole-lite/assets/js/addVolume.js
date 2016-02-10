var $replicas = $('#id_replicas'),
    $replicasGroup = $replicas.closest('.form-group'),
    $warning = $('<span class="help-block hidden"></span>');

$warning.text(__(
    "If one node of the cluster dies, " +
    "the data stored in this volume will become unavailable. " +
    "Recommended value: 2 or greater."));

$replicas
    .after($warning)
    .on('input', function (e) {
        var value = parseInt(e.target.value);
        if (value < 2) {
            $replicasGroup.addClass('has-warning');
            $warning.removeClass('hidden');
        } else {
            $replicasGroup.removeClass('has-warning');
            $warning.addClass('hidden');
        }
    });
