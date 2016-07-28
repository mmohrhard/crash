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

    String.prototype.beginsWith = function(string) {
        return(this.indexOf(string) === 0);
    }

    $(".threads").find("td:nth-child(4)").each(function() {
        var $this = $(this);
        var cellText = $this.html();
        var trimmedText = $.trim(cellText);
        var nonCoreFilePattern = new RegExp('^[a-zA-Z]:');
        if (trimmedText && trimmedText.length > 0 && !nonCoreFilePattern.test(trimmedText))
        {
            var url = "http://cgit.freedesktop.org/libreoffice/core/tree/" + trimmedText.replace(":", "?h=libreoffice-5-2#n");
            $this.html("<a href=\""+ url + "\">" + src_code_path + "</a>");
        }
    });

});
