        var socket;
        $(document).ready(function(){
            socket = io.connect('http://' + document.domain + ':' + location.port,{'reconnect' : true});
            socket.on('news', function(data) {
                console.log(data.num)
            });
            socket.on('socketlogout', function() {
                
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