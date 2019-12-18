self.addEventListener('push', function(event) {
    var data = "[無法讀取訊息]"
    try {
      data = event.data.text();
    } catch(e) {}
  
    var title = '您有新訊息';
    var body = data;
    var icon = '/img/icon.png';
    var tag = '';
  
    event.waitUntil(
      self.registration.showNotification(title, {
        body: body,
        icon: icon,
        tag: tag
      })
    );
  });
  
  // 使用者點擊推播彈跳訊息
  self.addEventListener('notificationclick', function(event) {
    var goingToOpenUrl = 'https://example.com';
    event.notification.close();
  
    event.waitUntil(clients.matchAll({
      type: 'window'
    }).then(function(clientList) {
      for (var i = 0; i < clientList.length; i++) {
        var client = clientList[i];
        if (client.url === goingToOpenUrl && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(goingToOpenUrl);
      } else {
        console.log("無法開啟url:"+goingToOpenUrl);
      }
    }));
  });