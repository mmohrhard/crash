$(document).ready(function() 
{ 
    $("#tabs").tabs();
    $("#os_tab").tabs();
    $("#cpu_tab").tabs();
    $("#version_tab").tabs();

    $("#data-table").tablesorter({sortList: [[1,1], [5,1]]});
} 
); 
