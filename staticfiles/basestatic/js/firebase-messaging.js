
var firebaseConfig = {
    apiKey: "AIzaSyC_qQi7TfgOv75WZ7YqNb_-4izqz7fqPa8",
    authDomain: "esyala-a8bae.firebaseapp.com",
    projectId: "esyala-a8bae",
    storageBucket: "esyala-a8bae.appspot.com",
    messagingSenderId: "695834964214",
    appId: "1:695834964214:web:31f56b6bc77038e29f3cd7",
    measurementId: "G-CWHGVYE9C6"
  };
  
  // Firebase'i başlat
  firebase.initializeApp(firebaseConfig);
  
  // Firebase Messaging nesnesi oluştur
  const messaging = firebase.messaging();
  
  // Token alma işlemi
  messaging.getToken({ vapidKey: 'BI_zyKhNuPkzLg25BQCSMU5Xv5MyjaUDMPy39Ex_QrX780ylj1KMpUTIadNQbz9Abw7UYYPkvH79mM5Hc95i5DU' })
    .then((currentToken) => {
      if (currentToken) {
        console.log('Token:', currentToken);
        sendTokenToServer(currentToken);  // Token'ı sunucuya gönder
      } else {
        console.log('No registration token available. Request permission to generate one.');
      }
    })
    .catch((err) => {
      console.log('An error occurred while retrieving token. ', err);
    });
  
  function sendTokenToServer(token) {
    const userAgent = navigator.userAgent;
    const platform = navigator.platform;
    const deviceType = /Mobi|Android/i.test(userAgent) ? 'mobile' : 'desktop';
  
    fetch('/save-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            token: token,
            user_agent: userAgent,
            platform: platform,
            device_type: deviceType
        }),
    }).then(response => {
        console.log('Token başarıyla sunucuya gönderildi.');
    }).catch((error) => {
        console.log('Token gönderimi hatası:', error);
    });
  }
  
  function getDeviceInfo() {
    const userAgent = navigator.userAgent; // Kullanıcının cihaz ve tarayıcı bilgileri
    const platform = navigator.platform;   // İşletim sistemi bilgisi
    const isMobile = /Mobi|Android/i.test(userAgent); // Mobil cihaz olup olmadığını kontrol et
    const deviceType = isMobile ? 'Mobile' : 'Desktop'; // Cihaz türünü belirle
    return { userAgent, platform, deviceType };
  }
  
  // Bildirim izinlerini isteme
  messaging
    .requestPermission()
    .then(function () {
      console.log("Bildirim izni verildi.");
      return messaging.getToken();
    })
    .catch(function (err) {
      console.log("Bildirim izni alınamadı.", err);
    });
  
  // Mesaj alındığında yapılacaklar
  messaging.onMessage((payload) => {
    console.log('Mesaj alındı: ', payload);
  });
  
  // Service Worker'ı kaydet
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/firebase-messaging-sw.js')
      .then(function(registration) {
        console.log('Service Worker registered with scope:', registration.scope);
      }).catch(function(error) {
        console.log('Service Worker registration failed:', error);
      });
  }
  