$(document).ready(function () {
    $(".addSwitch").click(function () {
        $.facebox($("#switchForm").tmpl({ add: true }));
    });

    $(".switches .edit").live("click", function () {
        var row = $(this).parents("tr:first");

        $.facebox($("#switchForm").tmpl({
            add:    false,
            curkey: row.attr("data-switch-key"),
            key:    row.attr("data-switch-key"),
            name:   row.attr("data-switch-name"),
            desc:   row.attr("data-switch-desc")
        }))
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
        var status = el.attr("data-status");        

        $.post(GARGOYLE.updateStatus,
            {
                key:    row.attr("data-switch-key"),
                status: status
            },

            function (response) {
                if (response.status == status) {
                    row.find(".toggled").removeClass("toggled");
                    el.addClass("toggled");
                }
            },
        "json");
    });

    $("#facebox .closeFacebox").live("click", function (ev) {
        ev.preventDefault();
        $.facebox.close();
    });

    $("#facebox .submitSwitch").live("click", function () {
        var action = $(this).attr("data-action");
        var curkey = $(this).attr("data-curkey");

        $.post(action == "add" ? GARGOYLE.addSwitch : GARGOYLE.updateSwitch,
            {
                curkey: curkey,
                name:   $("#facebox input[name=name]").val(),
                key:    $("#facebox input[name=key]").val(),
                desc:   $("#facebox textarea[name=desc]").val()
            },
            
            function (data) {
                var result = $("#switchData").tmpl(data);

                if (action == "add") {
                    $("table.switches tr:last").after(result);
                    $.facebox.close();
                } else {
                    $("table.switches tr[data-key=" + curkey + "]").replaceWith(result);
                    $.facebox.close();
                }
            },
        "json");
    });
});