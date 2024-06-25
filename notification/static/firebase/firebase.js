importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-messaging.js');

// Your web app's Firebase configuration
var firebaseConfig = {
  apiKey: "AIzaSyDj1YviC5nz_96MX1wqCZuir67QNsyWunY",
  authDomain: "ieee-nsu-sb-portal.firebaseapp.com",
  projectId: "ieee-nsu-sb-portal",
  storageBucket: "ieee-nsu-sb-portal.appspot.com",
  messagingSenderId: "608760512807",
  appId: "1:608760512807:web:8730f4f3588840636aa902",
  measurementId: "G-4G0H22SDX5"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
  };

  return self.registration.showNotification(notificationTitle, notificationOptions);
});
