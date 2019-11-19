        var socket;
        $(document).ready(function(){
            socket = io.connect('http://' + document.domain + ':' + location.port,{'reconnect' : true});
            socket.on('news', function(data) {
                console.log(data.num)
            });
        });