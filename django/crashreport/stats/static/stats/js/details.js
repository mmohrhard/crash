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
        var version_str = $.trim($(".version_str").html());
        var versionPattern = new RegExp(/(\d)\.(\d).(\d)\./);
        var [,...version_arr] = versionPattern.exec(version_str);
        
        // version_arr = [major, minor, patch]
        if(version_arr[2] === "0"){
            version_arr.pop();
        }
        version_str = version_arr.join('-');

        if (trimmedText && trimmedText.length > 0 && !nonCoreFilePattern.test(trimmedText))
        {
            var url = "http://cgit.freedesktop.org/libreoffice/core/tree/" 
                + trimmedText.replace(":", "?h=libreoffice-" + version_str +"#n");
            $this.html("<a href=\""+ url + "\">" + trimmedText + "</a>");
        }
    });

});
