$(document).ready(function () {
    $(".addSwitch").click(function () {
        $.facebox($("#addSwitch").tmpl({}));
    });

    $(".switches .delete").live("click", function () {
        var row = $(this).parents("tr:first");

        $.post(GARGOYLE.deleteSwitch,
            {
                key: row.attr("data-switch-key")
            },
            
            function (response) {
                if (response.success) {
                    row.remove();
                }
            },
        "json");
    });

    $(".switches td.status button").live("click", function () {
        var row = $(this).parents("tr:first");
        var el = $(this);

        $.post(GARGOYLE.updateStatus,
            {
                key:    row.attr("data-switch-key"),
                status: el.attr("data-status")
            },

            function (response) {
                if (response.status == status) {
                    row.find(".toggled").removeClass("toggled");
                    el.addClass("toggled");
                }
            },
        "json");
    });

    $("#facebox .closeFacebox").live("click", function () {
        $.facebox.close();
    });

    $("#facebox .submitSwitch").live("click", function () {
        $.post(GARGOYLE.addSwitch,
            {
                name: $("#facebox input[name=name]").val(),
                key:  $("#facebox input[name=key]").val(),
                desc: $("#facebox textarea[name=desc]").val()
            },
            
            function (data) {
                var result = $("#switchData").tmpl(data);
                $("table.switches tr:last").after(result);
                $.facebox.close();
            },
        "json");
    });
});