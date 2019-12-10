var socket;
var noti = false;
$(document).ready(function () {
  socket = io.connect('https://' + document.domain);
  socket.on('news', function (data) {
    console.log(data.num)

    if(!noti)
    {
      alertnotice(noti);
      noti =  true;
    }
    else{
      alertnotice(noti);
      noti = false; 
    }
    
  });
  socket.on('socketlogout', function () {

    $.ajax({
      url: "/logoutAPI",
      type: "POST",
      data: "",
      contentType: 'application/json; charset=utf-8',
      success: function () {
        window.alert('此帳號已從其他地方登入，即將將你登出')
        location.reload();
      },
      error: function () {
        console.log("return pos fail");
      }
    });
  });
});

function alertnotice(notice) {
  var x = document.getElementById("notice");
  var y = document.getElementById("menu");

  x.innerHTML = "新通知";

  function alertnoti() {
    x.setAttribute("class", "w3-bar-item w3-button w3-center w3-padding-16 w3-animate-zoom");
    setTimeout(function () { x.setAttribute("class", "w3-bar-item w3-button w3-center w3-padding-16") }, 1000);
  }
  function alertmenu() {
    y.setAttribute("class", "w3-right w3-button w3-border w3-animate-zoom");
    setTimeout(function () { y.setAttribute("class", "w3-right w3-button w3-border") }, 1000);
  }

  if(!notice)
  {
    setInterval(alertnoti, 1500);
    alertProgram = setInterval(alertmenu, 1500);
  }
  
  window.addEventListener("click", function () { clearInterval(alertProgram); y.setAttribute("class", "w3-right w3-button w3-border"); console.log("clear") }, false);

}