var lat, lng;
var pos = {
  lat: lat,
  lng: lng
}
function getCoords() {
    navigator.geolocation.watchPosition((position) => {
      console.log(position.coords);
      //lat = position.coords.latitude;
      //lng = position.coords.longitude;
      pos.lat = position.coords.latitude;
      pos.lng = position.coords.longitude;
      
      console.log(JSON.stringify(pos));
      $.ajax({
        url: "{{url_for('getLocation')}}",
        type: "post",
        data: JSON.stringify(pos),
        dataType: 'json',
        processData: false,
        contentType: false,
        success: function () {
          console.log("return pos success");
        },
        error: function () {
          console.log("return pos fail");
        }
      })
    });
  }