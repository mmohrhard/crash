$(document).ready(function () {
    $('a[href="#allthreads"]').on('click', function () {
        var element = $(this);
        $('#allthreads').toggle(400);
        if (element.text() === element.data('show')) {
            element.text(element.data('hide'));
            return true;
        } else {
            element.text(element.data('show'));
            location.hash = 'frames';
            return false;
        }
    });
});
