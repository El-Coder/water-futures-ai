// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAzAisQlEUKeIHTrpGy64eSm-ZRgduMMLQ",
  authDomain: "water-futures-ai.firebaseapp.com",
  projectId: "water-futures-ai",
  storageBucket: "water-futures-ai.firebasestorage.app",
  messagingSenderId: "640022295144",
  appId: "1:640022295144:web:3b7bb0826efb6ace0981dd",
  measurementId: "G-1PKETWJCV2"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };