function setDefaultPorts() {
    let ports = { 23: 23, 25: 25, 53: 53, 80: 80, 110: 110, 143: 143, 161: 161, 443: 443 };
    setInStorage("ports", JSON.stringify(ports));
}

function addPort(port) {
    if (port !== "" && Number.isInteger(parseInt(port))) {
        updateSelectPorts(port);
        $('#new_port').val('');
    }
}

function updateSelectPorts(port) {
    $('#ports_select').append("<option value='" + port + "' selected>" + port + "</option>");
    $('select').formSelect();
}

function resetResultsTable() {
    $('#tableHeaderRow').empty();
    $('#tableBody').empty();
    $('#tableHeaderRow').append("<th>Name</th><th>IP</th>");
}

function formatResult(result) {
    if (result === -1) {
        return "<i class='material-icons red-text'>remove_circle</i>";
    } else if (result === "OK") {
        return "<i class='material-icons green-text'>check_circle</i>";
    } else {
        return Math.round(result * 100000) / 100 + "ms";
    }
}

function goToPage1() {
    M.Tabs.getInstance(document.querySelector('.tabs')).select('scanner');
}

function goToPage2() {
    M.Tabs.getInstance(document.querySelector('.tabs')).select('results');
    initTableHeight();
}

function goToPage3() {
    M.Tabs.getInstance(document.querySelector('.tabs')).select('warnings');
}

function goToPage4() {
    M.Tabs.getInstance(document.querySelector('.tabs')).select('report');
}

function initTableHeight() {
    $("#resultsTable").css({
        'max-height': $(window).height() - 133 + "px",
        'height': $(window).height() - 133 + "px",
    });

    $("#scanner").css({
        'max-height': $(window).height() - 133 + "px",
        'height': $(window).height() - 133 + "px",
    });
}

function makeInputsJSON(UI = true) {
    return JSON.stringify({
        "ports": getSelectedPorts(),
        "check-links": $("#scanLinks:checked").length == 1,
        "timeout": parseInt($("#timeout").val()),
        "dns-input-file": $("#input_dns_file").val(),
        "UI": UI,
        "alert-triggers": {
            "new-entry": $("#altr-new-entry:checked").length == 1,
            "changed-dns-record": $("#altr-changed-dns-record:checked").length == 1,
            "different-open-ports": $("#altr-different-open-ports:checked").length == 1,
            "new-warnings-only": $("#altr-new-warnings-only:checked").length == 1,
            "all-warnings": $("#altr-all-warnings:checked").length == 1,
            "unexpected-state": $("#altr-unexpected-state:checked").length == 1,
        },
        "email-address": $("#altr-email-address").val(),
        "mail-server": $("#altr-mail-server").val(),
        "mail-server-port": $("#altr-mail-server-port").val(),
        "mail-server-auth": $("#altr-mail-server-auth").val(),
        "mail-server-pass": $("#altr-mail-server-pass").val()
    });
}

function formContainsErrors() {
    let ports = getSelectedPorts();
    let inputFile = $("#input_dns_file").val();
    let emailAddress = $("#altr-email-address").val();

    let error = false;

    if (emailAddress.length == 0) {
        $("#altr-email-address").addClass("invalid");
        error = true;
    }

    // if (ports.length == 0) {
    //     $("#ports_select").parent().find("input.select-dropdown").addClass("invalid");
    //     error = true;
    // }

    return error;
}

var finish = false;

function stop() {
    finish = true;
    $("#stop-program").find("i").css("animation", "spin 2s infinite linear");
}

function addIP(ipRange, portsRange, timeout, response) {
    let error = false;

    const regexIP = /((([0-9]{1,3})\-)?([0-9]{1,3});)*(([0-9]{1,3})\-)?([0-9]{1,3})\.((([0-9]{1,3})\-)?([0-9]{1,3});)*(([0-9]{1,3})\-)?([0-9]{1,3})\.((([0-9]{1,3})\-)?([0-9]{1,3});)*(([0-9]{1,3})\-)?([0-9]{1,3})\.((([0-9]{1,3})\-)?([0-9]{1,3});)*(([0-9]{1,3})\-)?([0-9]{1,3})/;
    ip = ipRange.match(regexIP)
    if (ip === null) {
        $("#perip-ip-range").addClass("invalid");
        error = true;
    }

    const regexPorts = /(([0-9]{1,5}-)?([0-9]{1,5});)*(([0-9]{1,5}-)?([0-9]{1,5}))/;
    ports = portsRange.match(regexPorts)
    if (ports === null) {
        $("#perip-ports-range").addClass("invalid");
        error = true;
    }

    if (timeout.length === 0 || parseInt(timeout) <= 0 || parseInt(timeout) > 30) {
        $("#perip-timeout").addClass("invalid");
        error = true;
    }

    if (!error) {
        $("#perip-ip-range").removeClass("invalid");
        $("#perip-ip-range").val("");
        $("#perip-ports-range").removeClass("invalid");
        $("#perip-ports-range").val("");
        $("#perip-timeout").removeClass("invalid");
        $("#perip-timeout").val("");
        console.log(ip[0] + "/" + ports[0] + "/" + timeout + "/" + response + "\n")

        $("#perip-txt").val($("#perip-txt").val() + ip[0] + "/" + ports[0] + "/" + timeout + "/" + response + "\n");

        eel.save_ips($("#perip-txt").val());
        M.textareaAutoResize($("#perip-txt"));
    }
}

function editIpRanges() {
    if ($("#perip-txt").hasClass("editable")) {
        $("#perip-txt").attr("readonly", "readonly");
        $("#perip-txt").removeClass("editable");
        $("#edit-perip-txt").html("edit");
        eel.save_ips($("#perip-txt").val());
        Swal.fire({
            title: 'Saved!',
            type: 'success',
            timer: 1000
        })
    } else {
        $("#perip-txt").removeAttr("readonly");
        $("#perip-txt").addClass("editable");
        $("#edit-perip-txt").html("save");
        Swal.fire(
            'Careful!',
            'Your raw modifications are not checked for syntax errors. Use the form above to add IPs.\nDon\'t forget to save your changes',
            'warning'
        )
    }
}

$(document).ready(function () {
    
    M.AutoInit();
    initTableHeight();

    $('#new_port').keyup(function(e){
        if(e.keyCode == 13)
        {
            addPort($('#new_port').val())
        }
    });

});
