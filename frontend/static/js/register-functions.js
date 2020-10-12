$(document).ready(function () {
  $("#register").click(function (e) {
    console.log("register service");
    register();
  })


  function register() {
    var giturl = $("#git_url").val();
    console.log(giturl)
    var data = {
      "giturl": giturl
    };
    $.ajax({
      type: "POST",
      data: JSON.stringify(data),
      url: url_register,
      dataType: "json",
      contentType: 'application/json',
      beforeSend: function () {
        document.getElementById("loader").style.display = "block";
      },
      success: function (data) {
        alert("Sucess!");
        document.getElementById("loader").style.display = "none";
        location.reload();
      },
      error: function (data) {
        alert("Error! Please contact your admin. "+ data.responseText);
        console.log("error");
        document.getElementById("loader").style.display = "none";
      }
    });
  }

})