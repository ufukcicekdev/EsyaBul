
importScripts('https://www.gstatic.com/firebasejs/10.13.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.1/firebase-messaging.js');

const firebaseConfig = {
    apiKey: "AIzaSyC_qQi7TfgOv75WZ7YqNb_-4izqz7fqPa8",
    authDomain: "esyala-a8bae.firebaseapp.com",
    projectId: "esyala-a8bae",
    storageBucket: "esyala-a8bae.appspot.com",
    messagingSenderId: "695834964214",
    appId: "1:695834964214:web:31f56b6bc77038e29f3cd7",
    measurementId: "G-CWHGVYE9C6"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log('[firebase-messaging-sw.js] Received background message ', payload);
    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: payload.notification.icon
    });
});
