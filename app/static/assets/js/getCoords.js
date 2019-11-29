var lat, lng;
var pos = {
  "lat": lat,
  "lng": lng
}
function initMap() {
  navigator.geolocation.watchPosition((position) => {
    console.log(position.coords);
    //lat = position.coords.latitude;
    //lng = position.coords.longitude;
    pos.lat = position.coords.latitude;
    pos.lng = position.coords.longitude;
      
    console.log(JSON.stringify(pos));
    $.ajax({
      url: "/getLocation",
      type: 'POST',
      data: JSON.stringify(pos),
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