$(document).ready(function () {


  webinterfaceButton = document.getElementById("button-webinterface");

  check_status();
  $("#restart").click(function (e) {
    console.log("restarting service");
    service_func("restart");
  })

  $("#stop").click(function (e) {
    console.log("stopping service");
    service_func("stop");
  })
  $("#build").click(function (e) {
    console.log("building service");
    service_func("build");
  })

  $("#uninstall").click(function (e) {
    console.log("uninstalling service");
    service_func("uninstall");
  })

  $("#refresh-logs").click(function (e) {
    console.log("updating logs");
    update_logs();
  })

  $("#save-config").click(function (e) {
    save_config();
  })

  $("#save-port").click(function (e) {
    save_port();
  })

  $("#restore-config").click(function (e) {
    cm_config.setValue(JSON.stringify(restore_config_text));
    format_cm_config();
  })


  function save_config() {
    var data = cm_config.getValue(" ");
    var data = {
      "tag": tag,
      "config": data
    };
    $.ajax({
      type: "POST",
      data: JSON.stringify(data),
      url: url_config,
      dataType: "json",
      contentType: 'application/json',
      beforeSend: function () {
        document.getElementById("loader").style.display = "block";
      },
      success: function (data) {
        console.log(data)
        document.getElementById("loader").style.display = "none";
      },
      error: function (data) {
        alert("Error!\n" + data.responseText);
        document.getElementById("loader").style.display = "none";
      }
    });
  }

  function save_port() {
    var port = $("#port").val();
    var container_port = document.getElementById("container_port").innerText
    var data = {};
    data[container_port] = port;
    var data = {
      "tag": tag,
      "port": data
    };
    if (port != "") {
      $.ajax({
        type: "POST",
        data: JSON.stringify(data),
        url: url_port,
        dataType: "json",
        contentType: 'application/json',
        beforeSend: function () {
          document.getElementById("loader").style.display = "block";
        },
        success: function (data) {
          console.log(data);
          document.getElementById("loader").style.display = "none";
        },
        error: function (data) {
          alert("Error! Please contact your admin. " + data.responseText);
          document.getElementById("loader").style.display = "none";
        }
      });
    }
  }


  function service_func(func) {
    var data = {
      "tag": tag,
      "function": func
    };
    $.ajax({
      type: "POST",
      data: JSON.stringify(data),
      url: url,
      dataType: "json",
      contentType: 'application/json',
      beforeSend: function () {
        document.getElementById("loader").style.display = "block";
      },
      success: function (data) {
        check_status();
        document.getElementById("loader").style.display = "none";
      },
      error: function (data) {
        alert("Error! Please contact your admin. " + data.responseText);
        document.getElementById("loader").style.display = "none";
      }
    });
  }

  function check_status() {
    var data = {
      "tag": tag,
      "function": "status"
    };
    $.ajax({
      type: "POST",
      data: JSON.stringify(data),
      url: url,
      dataType: "json",
      contentType: 'application/json',
      success: function (data) {
        var button = document.getElementById("web");
        if (data["message"]) {
          // service is running
          document.getElementById("status").style.color = "lightgreen";
          document.getElementById("restart").innerHTML = '<i class="fas fa-redo fa-sm text-white-50" id="restart-icon"></i> <div id="restart-text" style="display:inline;">&nbsp;&nbsp;Restart</div>';
          button.style.pointerEvents = "auto";
          button.classList.remove("btn-outline-primary");
          button.classList.add("btn-primary");

        } else {
          // service is not running
          document.getElementById("status").style.color = "red";
          document.getElementById("restart").innerHTML = '<i class="fas fa-play fa-sm text-white-50" id="restart-icon"></i> <div id="restart-text" style="display:inline;">&nbsp;&nbsp;Start</div>';
          console.log(webinterfaceButton);
          button.style.pointerEvents = "none";
          button.classList.remove("btn-primary");
          button.classList.add("btn-outline-primary");
        }
      },
      error: function (data) {
        alert("Error! Please contact your admin. " + data.responseText);
      }
    });
  }

  function update_logs() {

    var data = {
      "tag": tag,
      "function": "logs"
    };
    $.ajax({
      type: "POST",
      data: JSON.stringify(data),
      url: url,
      dataType: "json",
      contentType: 'application/json',
      beforeSend: function () {
        document.getElementById("loader").style.display = "block";
      },
      success: function (data) {
        cm_logs.setValue(data["message"]["logs"]);
        cm_logs.focus();
        cm_logs.setCursor(cm_logs.lineCount(), 0);
        document.getElementById("loader").style.display = "none";
      },
      error: function (data) {
        document.getElementById("loader").style.display = "none";
        alert("Could not read logs from service.");
      }
    });
  }
});

// CODEMIRROR
//--------------------------------------------------------------------------

(function () {

  CodeMirror.extendMode("css", {
    commentStart: "/*",
    commentEnd: "*/",
    newlineAfterToken: function (type, content) {
      return /^[;{}]$/.test(content);
    }
  });

  CodeMirror.extendMode("javascript", {
    commentStart: "/*",
    commentEnd: "*/",
    // FIXME semicolons inside of for
    newlineAfterToken: function (type, content, textAfter, state) {
      if (this.jsonMode) {
        return /^[\[,{]$/.test(content) || /^}/.test(textAfter);
      } else {
        if (content == ";" && state.lexical && state.lexical.type == ")") return false;
        return /^[;{}]$/.test(content) && !/^;/.test(textAfter);
      }
    }
  });

  CodeMirror.extendMode("xml", {
    commentStart: "<!--",
    commentEnd: "-->",
    newlineAfterToken: function (type, content, textAfter) {
      return type == "tag" && />$/.test(content) || /^</.test(textAfter);
    }
  });

  // Comment/uncomment the specified range
  CodeMirror.defineExtension("commentRange", function (isComment, from, to) {
    var cm = this,
      curMode = CodeMirror.innerMode(cm.getMode(), cm.getTokenAt(from).state).mode;
    cm.operation(function () {
      if (isComment) { // Comment range
        cm.replaceRange(curMode.commentEnd, to);
        cm.replaceRange(curMode.commentStart, from);
        if (from.line == to.line && from.ch == to.ch) // An empty comment inserted - put cursor inside
          cm.setCursor(from.line, from.ch + curMode.commentStart.length);
      } else { // Uncomment range
        var selText = cm.getRange(from, to);
        var startIndex = selText.indexOf(curMode.commentStart);
        var endIndex = selText.lastIndexOf(curMode.commentEnd);
        if (startIndex > -1 && endIndex > -1 && endIndex > startIndex) {
          // Take string till comment start
          selText = selText.substr(0, startIndex)
            // From comment start till comment end
            +
            selText.substring(startIndex + curMode.commentStart.length, endIndex)
            // From comment end till string end
            +
            selText.substr(endIndex + curMode.commentEnd.length);
        }
        cm.replaceRange(selText, from, to);
      }
    });
  });

  // Applies automatic mode-aware indentation to the specified range
  CodeMirror.defineExtension("autoIndentRange", function (from, to) {
    var cmInstance = this;
    this.operation(function () {
      for (var i = from.line; i <= to.line; i++) {
        cmInstance.indentLine(i, "smart");
      }
    });
  });

  // Applies automatic formatting to the specified range
  CodeMirror.defineExtension("autoFormatRange", function (from, to) {
    var cm = this;
    var outer = cm.getMode(),
      text = cm.getRange(from, to).split("\n");
    var state = CodeMirror.copyState(outer, cm.getTokenAt(from).state);
    var tabSize = cm.getOption("tabSize");

    var out = "",
      lines = 0,
      atSol = from.ch == 0;

    function newline() {
      out += "\n";
      atSol = true;
      ++lines;
    }

    for (var i = 0; i < text.length; ++i) {
      var stream = new CodeMirror.StringStream(text[i], tabSize);
      while (!stream.eol()) {
        var inner = CodeMirror.innerMode(outer, state);
        var style = outer.token(stream, state),
          cur = stream.current();
        stream.start = stream.pos;
        if (!atSol || /\S/.test(cur)) {
          out += cur;
          atSol = false;
        }
        if (!atSol && inner.mode.newlineAfterToken &&
          inner.mode.newlineAfterToken(style, cur, stream.string.slice(stream.pos) || text[i + 1] || "", inner.state))
          newline();
      }
      if (!stream.pos && outer.blankLine) outer.blankLine(state);
      if (!atSol) newline();
    }

    cm.operation(function () {
      cm.replaceRange(out, from, to);
      for (var cur = from.line + 1, end = from.line + lines; cur <= end; ++cur)
        cm.indentLine(cur, "smart");
      cm.setSelection(from, cm.getCursor(false));
    });

    cm.setCursor(0, 0);
  });
})();

var cm_config = CodeMirror.fromTextArea(document.getElementById("service-config"), {
  mode: "application/ld+json",
  matchBrackets: true,
  lineNumbers: true,
  lineWrapping: true
});
format_cm_config();

function format_cm_config() {
  var totalLines = cm_config.lineCount();
  cm_config.autoFormatRange({
    line: 0,
    ch: 0
  }, {
    line: totalLines
  });


}

var cm_logs = CodeMirror.fromTextArea(document.getElementById("service-logs"), {
  mode: "application/json",
  matchBrackets: true,
  lineWrapping: true,
  readOnly: true
});

// Set the cursor at the end of existing content
cm_logs.focus();
cm_logs.setCursor(cm_logs.lineCount(), 0);

$('html,body').scrollTop(0);