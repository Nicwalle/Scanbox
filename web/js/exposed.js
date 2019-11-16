eel.expose(getSelectedPorts);
eel.expose(addScannedIP);
eel.expose(incrementScanned);
eel.expose(addMessage);
eel.expose(updateTotalIPs);
eel.expose(isStopped);
eel.expose(terminate);
eel.expose(addError);
eel.expose(fillInFields);
eel.expose(printReport)

function getSelectedPorts() {
    let stringPorts = M.FormSelect.getInstance(document.querySelector('#ports_select')).getSelectedValues();
    let ports = stringPorts.map(x => parseInt(x));
    ports.sort(function(a, b){return a-b});
    return ports;
}

function addScannedIP(scan_result, ports) {
    parsed_scan_result = JSON.parse(scan_result);
    
    if ($('#tableHeaderRow').children().length === 2) {
        ports.forEach(function(port) {
            $('#tableHeaderRow').append("<th>"+ port +"</th>")
        })
    }

    let str = "<tr>";
    if (parsed_scan_result.type == "DNS") {
        str += "<td>" + parsed_scan_result.record.name + "</td>";
        str += "<td>" + parsed_scan_result.record.data + "</td>";
    } else if (parsed_scan_result.type == "IP") {
        str += "<td>NONE</td>";
        str += "<td>" + parsed_scan_result.record.ip + "</td>";
    }
    console.log(ports)
    console.log(parsed_scan_result.ports);
    ports.forEach(function(port) {
        console.log(port);
        
        if (port in parsed_scan_result.ports) {
            str += "<td>" + formatResult(parsed_scan_result.ports[port]) + "</td>";
        } else {
            str += "<td></td>";
        }
    })

        
    str += "</tr>";
    $('#tableBody').append(str);
    $('#page2Loader').hide();
    var elem = document.getElementById('resultsTable');
    elem.scrollTop = elem.scrollHeight;
}

function incrementScanned() {
    $('.scannedIPs .passed').html(parseInt($('.scannedIPs .passed').html()) + 1);
}

function addMessage(scanMessage) {
    parsedMessage = JSON.parse(scanMessage);
    console.log(parsedMessage)

    let str =   "<li>";
    str +=          "<div class='collapsible-header'>";
    str +=              "<i class='material-icons'>"+ parsedMessage["type"] +"</i>";
    str +=              "<strong>[" + parsedMessage["time"] + "]</strong>&nbsp;";
    str +=              parsedMessage["title"];
    str +=          "</div>";
    str +=          "<div class='collapsible-body'>";
    str +=              "<span>" + parsedMessage["message"] + "</span>";
    str +=          "</div>";
    str +=      "</li>";
    $('#resultsMessages').append(str);
    $('#page3Loader').hide();
}

function updateTotalIPs(total) {
    $(".scannedIPs").removeClass("hide");
    $(".scannedIPs .total").html(total);
}

function isStopped() {
    return finish;
}

function terminate() {
    $("#stop-program").parent().hide();
    $("#restart-program").parent().removeClass("hide");
    Swal.fire({
        type: 'success',
        title: 'Scanbox',
        text: 'Scan terminated with success, you can check the results in the "OPEN PORTS", "MESSAGES" and "REPORT" tabs'
      })
}

function addError(error) {
    parsedError = JSON.parse(error);
    if (parsedError["type"] == "file-error") {
        $("#file-error").html(parsedError["message"]);
    }
    $("#startScan").removeAttr("disabled");
}

function printReport(report) {
    $("#report-text").html(report);
}

function fillInFields(jsonInputs, ipsInput) {
    jsonInputs = JSON.parse(jsonInputs)

    // Ports to scan
    let $ports_select = $("#ports_select");
    $ports_select.empty();
    ports = jsonInputs["ports"]
    for (let key in ports) {
        $ports_select.append("<option value='" + ports[key] + "' selected>" + ports[key] + "</option>")
    }
    $('select').formSelect();

    // Scan links on web page
    if (jsonInputs["check-links"]) {
        $("#scanLinks").attr("checked", "checked");
    }

    // Timeout
    $("#timeout").val(jsonInputs["timeout"]);

    // DNS file path
    $("#input_dns_file").val(jsonInputs["dns-input-file"]);

    // Input IPs
    $("#perip-txt").html(ipsInput);

    // Email to alert
    $("#altr-email-address").val(jsonInputs["email-address"]);

    // Mailserver to use
    $("#altr-mail-server").val(jsonInputs["mail-server"]);

    // Mailserver port
    $("#altr-mail-server-port").val(jsonInputs["mail-server-port"]);

    // Mailserver auth
    $("#altr-mail-server-auth").val(jsonInputs["mail-server-auth"]);

    // Mailserver pass
    $("#altr-mail-server-pass").val(jsonInputs["mail-server-pass"]);

    // Alert trigger: New Entry
    if (jsonInputs["alert-triggers"]["new-entry"]) {
        $("#altr-new-entry").attr("checked", "checked");
    }

    // Alert trigger: Changed DNS record
    if (jsonInputs["alert-triggers"]["changed-dns-record"]) {
        $("#altr-changed-dns-record").attr("checked", "checked");
    }

    // Alert trigger: Different open ports since last scan
    if (jsonInputs["alert-triggers"]["different-open-ports"]) {
        $("#altr-different-open-ports").attr("checked", "checked");
    }

    // Alert trigger: New warnings only
    if (jsonInputs["alert-triggers"]["new-warnings-only"]) {
        $("#altr-new-warnings-only").attr("checked", "checked");
    }

    // Alert trigger: All warnings
    if (jsonInputs["alert-triggers"]["all-warnings"]) {
        $("#altr-all-warnings").attr("checked", "checked");
    }

    // Alert trigger: Unexpected port state
    if (jsonInputs["alert-triggers"]["unexpected-state"]) {
        $("#altr-unexpected-state").attr("checked", "checked");
    }

    M.updateTextFields();
    M.textareaAutoResize($("#perip-txt"));

}