// import * as SimplePeer from 'simple-peer';
// from "./quickstart-web-js-npm/node_modules/deepar" import * as deepar;

//const deepar = require('deepar');

// DOM Elements
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const connectButton = document.getElementById('connectButton');
const offerTextarea = document.getElementById('offerTextarea');
const answerTextarea = document.getElementById('answerTextarea');
const playLocalButton = document.getElementById('playLocalButton');
const playRemoteButton = document.getElementById('playRemoteButton');

let peer;
let deepARInstance = null;

// Initialize DeepAR if available
async function initDeepAR(stream) {
  const previewElement = document.getElementById('ar-screen'); // Set the element where AR will be displayed

  const effectList = [
      "effects/Vendetta_Mask.deepar", // Add more effects here if needed
  ];

  let deepARInstance = null;

  try {
        // Initialize DeepAR
        deepARInstance = await deepar.initialize({
            licenseKey: "cb2d5da261a7cab1dc27d69f78aba5f9e57baca5a6c1aaa58d5c0316f20df5fa1b2210fff7b8d894", // Your DeepAR license key
            previewElement, // The element that will show the AR video
            effect: effectList[0], // Initial AR effect
            rootPath: "./node_modules/deepar", // Path to DeepAR resources (optional, for custom deployment)
            additionalOptions: {
                cameraConfig: {
                    // You can configure the camera, e.g., facingMode: 'environment' for rear camera
                },
            },
        });

        // If initialization is successful, the AR effect will start
        console.log("DeepAR initialized successfully");
        document.getElementById('ar-screen').style.display = "block"; // Show the AR screen

        deepARInstance.startARFromStream(stream);
        console.log('DeepAR AR stream started with user media stream.');

    } catch (error) {
        console.error("Error initializing DeepAR:", error);
        document.getElementById("permission-denied-screen").style.display = "block"; // Show error screen
    }
}

// Get user media
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
  .then(stream => {
    // Display local video stream
    playLocalButton.addEventListener('click', () => {
      localVideo.srcObject = stream;
      localVideo.muted = true;
      localVideo.play();

      // Initialize DeepAR after local video starts
      initDeepAR(stream);
    });

    // Initialize SimplePeer instance
    peer = new SimplePeer({ initiator: location.hash === '#1', trickle: false, stream });

    // Handle signal data
    peer.on('signal', data => {
      const signalString = JSON.stringify(data);
      if (peer.initiator) {
        offerTextarea.value = signalString; // Show offer
      } else {
        answerTextarea.value = signalString; // Show answer
      }
    });

    // Display remote stream
    peer.on('stream', remoteStream => {
      playRemoteButton.addEventListener('click', () => {
        remoteVideo.srcObject = remoteStream;
        remoteVideo.muted = true;
        remoteVideo.play();
      });
    });
  })
  .catch(err => console.error('Error accessing media devices:', err));

// Handle connection button click
connectButton.addEventListener('click', () => {
  const signalData = peer.initiator ? answerTextarea.value : offerTextarea.value;
  try {
    peer.signal(JSON.parse(signalData));
  } catch (err) {
    console.error('Invalid signal data:', err);
  }
});
