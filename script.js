// Import SimplePeer
import * as deepar from "deepar";

// DOM Elements
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const connectButton = document.getElementById('connectButton');
const offerTextarea = document.getElementById('offerTextarea');
const answerTextarea = document.getElementById('answerTextarea');

let peer;

const playLocalWithMaskButton = document.getElementById('playLocalWithMask');
const playRemoteWithMaskButton = document.getElementById('playRemoteWithMask');

let deepARLocal, deepARRemote;
const effectPath = "effects/Vendetta_Mask.deepar";

// Initialize DeepAR for a given video element
async function initializeDeepAR(videoElement) {
  // const deepAR = await deepar.initialize({
  //   licenseKey: "0ee764525748b902349ccde3c9970f5c1fed1300eae370ee310597a0aec39cd4c6569049a9481f6a",
  //   previewElement: videoElement,
  //   effect: effectPath,
  //   rootPath: "./deepar-resources",
  // });
  deepAR = await deepar.initialize({
    licenseKey: "0ee764525748b902349ccde3c9970f5c1fed1300eae370ee310597a0aec39cd4c6569049a9481f6a",
    previewElement,
    effect: effectList[0],
    // Removing the rootPath option will make DeepAR load the resources from the JSdelivr CDN,
    // which is fine for development but is not recommended for production since it's not optimized for performance and can be unstable.
    // More info here: https://docs.deepar.ai/deepar-sdk/platforms/web/tutorials/download-optimizations/#custom-deployment-of-deepar-web-resources
    rootPath: "./deepar-resources",
    additionalOptions: {
      cameraConfig: {
        // facingMode: 'environment'  // uncomment this line to use the rear camera
      },
    },
  });
  return deepAR;
}

// Get user media
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
  .then(async(stream) => {
    // Display local video stream
    deepARLocal = await initializeDeepAR(localVideo);
    localVideo.srcObject = stream;

    playLocalWithMaskButton.addEventListener('click', async () => {
      await deepARLocal.switchEffect(effectPath);
      localVideo.play();
    });
    // playLocalButton.addEventListener('click', ()=>{
    //   localVideo.srcObject = stream;
    //   localVideo.muted = true;
    //   localVideo.play();


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
    peer.on('stream', async(remoteStream) => {
      playRemoteButton.addEventListener('click', async ()=>{
        remoteVideo.srcObject = remoteStream;
        remoteVideo.muted = true;
        deepARRemote = await initializeDeepAR(remoteVideo);

      playRemoteWithMaskButton.addEventListener('click', async () => {
        await deepARRemote.switchEffect(effectPath);
        remoteVideo.play();
        // remoteVideo.play();
      })
    });
  });
  })

// Handle connection button click
connectButton.addEventListener('click', () => {
  const signalData = peer.initiator ? answerTextarea.value : offerTextarea.value;
  try {
    peer.signal(JSON.parse(signalData));
  } catch (err) {
    console.error('Invalid signal data:', err);
  }
});
