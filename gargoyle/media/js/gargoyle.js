$(document).ready(function () {
    var api = function (url, params, succ) {
        $('#status').show();
        $.ajax({
            url: url,
            type: "POST",
            data: params,
            dataType: "json",
            success: function (resp) {
                $('#status').hide();

                if (resp.success) {
                    succ(resp.data);
                } else {
                    alert(resp.data);
                }
            },
            failure: function() {
                $('#status').hide();
                alert('There was an internal error. Data probably wasn\'t saved');
            }
        });
    };

    // Events

    $(".addSwitch").click(function (ev) {
        ev.preventDefault();
        $.facebox($("#switchForm").tmpl({ add: true }));
    });

    $(".switches tr").live("click", function (ev) {
        if (ev.target.tagName == 'A' || ev.target.tagName == 'INPUT' || ev.target.tagName == 'LABEL') {
            return;
        }
        var $this = $(this);
        $(".switches tr").each(function (_, el) {
            var $el = $(el);
            if (el == $this.get(0)) {
                $el.removeClass("collapsed");
            } else {
                $el.addClass("collapsed");
            }
        });
    });

    $(".switches .edit").live("click", function () {
        var row = $(this).parents("tr:first");

        $.facebox($("#switchForm").tmpl({
            add:    false,
            curkey: row.attr("data-switch-key"),
            key:    row.attr("data-switch-key"),
            name:   row.attr("data-switch-name"),
            desc:   row.attr("data-switch-desc")
        }));
    });

    $(".switches .delete").live("click", function () {
        var row = $(this).parents("tr:first");
        var table = row.parents("table:first");

        api(GARGOYLE.deleteSwitch, { key: row.attr("data-switch-key") },
            function () {
                row.remove();
                if (!table.find("tr").length) {
                    $("div.noSwitches").show();
                }
            });
    });

    $(".switches td.status button").live("click", function () {
        var row = $(this).parents("tr:first");
        var el = $(this);
        var status = el.attr("data-status");
        var labels = {
            4: "(Inherit from parent)",
            3: "(Active for everyone)",
            2: "(Active for conditions)",
            1: "(Disabled for everyone)"
        };

        if (status == 3) {
            if (!confirm('Are you SURE you want to enable this switch globally?')) {
                return;
            }
        }

        api(GARGOYLE.updateStatus,
            {
                key:    row.attr("data-switch-key"),
                status: status
            },

            function (swtch) {
                if (swtch.status == status) {
                    row.find(".toggled").removeClass("toggled");
                    el.addClass("toggled");
                    if ($.isArray(swtch.conditions) && swtch.conditions.length < 1 && swtch.status == 2) {
                        swtch.status = 3;
                    }
                    row.find('.status p').text(labels[swtch.status]);
                }
            });
    });

    $("p.addCondition a").live("click", function (ev) {
        ev.preventDefault();
        var form = $(this).parents("td:first").find("div.conditionsForm:first");

        if (form.is(":hidden")) {
            form.html($("#switchConditions").tmpl({}));
            form.addClass('visible');
        } else {
            form.removeClass('visible');
        }
    });

    $("div.conditionsForm select").live("change", function () {
        var field = $(this).val().split(",");
        $(this).
            parents("tr:first").
            find("div.fields").hide();

        $(this).
            parents("tr:first").
            find("div[data-path=" + field[0] + "." + field[1] + "]").show();
    });

    $("div.conditionsForm form").live("submit", function (ev) {
        ev.preventDefault();

        var data = {
            key: $(this).parents("tr:first").attr("data-switch-key"),
            id: $(this).attr("data-switch"),
            field: $(this).attr("data-field")
        };

        $.each($(this).find("input"), function () {
            var val;

            if ($(this).attr('type') == 'checkbox') {
                val = $(this).is(':checked') ? '1' : '0';
            } else {
                val = $(this).val();
            }
            data[$(this).attr("name")] = val;
        });

        api(GARGOYLE.addCondition, data, function (swtch) {
            var result = $("#switchData").tmpl(swtch);
            $("table.switches tr[data-switch-key="+ data.key + "]").replaceWith(result);
        });
    });

    $("div.conditions span.value a.delete-condition").live("click", function (ev) {
        ev.preventDefault();

        var el = $(this).parents("span:first");

        var data = {
            key:   el.parents("tr:first").attr("data-switch-key"),
            id:    el.attr("data-switch"),
            field: el.attr("data-field"),
            value: el.attr("data-value")
        };

        api(GARGOYLE.delCondition, data, function (swtch) {
            var result = $("#switchData").tmpl(swtch);
            $("table.switches tr[data-switch-key="+ data.key + "]").replaceWith(result);
        });

    });

    $("#facebox .closeFacebox").live("click", function (ev) {
        ev.preventDefault();
        $.facebox.close();
    });

    $("#facebox .submitSwitch").live("click", function () {
        var action = $(this).attr("data-action");
        var curkey = $(this).attr("data-curkey");

        api(action == "add" ? GARGOYLE.addSwitch : GARGOYLE.updateSwitch,
            {
                curkey: curkey,
                name:   $("#facebox input[name=name]").val(),
                key:    $("#facebox input[name=key]").val(),
                desc:   $("#facebox textarea").val()
            },

            function (swtch) {
                var result = $("#switchData").tmpl(swtch);

                if (action == "add") {
                    if ($("table.switches tr").length === 0) {
                        $("table.switches").html(result);
                        $("table.switches").removeClass("empty");
                        $("div.noSwitches").hide();
                    } else {
                        $("table.switches tr:last").after(result);
                    }

                    $.facebox.close();
                } else {
                    $("table.switches tr[data-switch-key=" + curkey + "]").replaceWith(result);
                    $.facebox.close();
                }
                result.click();
            }
        );
    });

    $('.search input').keyup(function () {
        var query = $(this).val();
        $('.switches tr').removeClass('hidden');
        if (!query) {
            return;
        }
        $('.switches tr').each(function (_, el) {
            var $el = $(el);
            var score = 0;
            score += $el.attr('data-switch-key').score(query);
            score += $el.attr('data-switch-name').score(query);
            if ($el.attr('data-switch-description')) {
                score += $el.attr('data-switch-description').score(query);
            }
            if (score === 0) {
                $el.addClass('hidden');
            }
        });
    });
});
