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
        url: "/getLocation",
        type: "post",
        data: JSON.stringify(pos),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function () {
          console.log("return pos success");
        },
        error: function () {
          console.log("return pos fail");
        }
      })
    });
  }