var $form = $('.js-form'),
    $inv = $form.find('.js-form-invite'),
    $pass = $form.find('.js-form-password'),
    $option = $form.find('input[name=option]');


$option.on('change', function (e) {
    switch (e.target.value) {
        case 'invite':
            $inv.removeClass('hidden');
            $pass.addClass('hidden');
            break;
        case 'set_password':
            $inv.addClass('hidden');
            $pass.removeClass('hidden');
            break;
        default:
            throw new Error('Unknown option: ' + e.target.value);
    }
})

/* Apply current option */
$option.filter('[checked]').change();
