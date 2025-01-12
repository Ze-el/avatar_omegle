// Import SimplePeer

// DOM Elements
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const connectButton = document.getElementById('connectButton');
const offerTextarea = document.getElementById('offerTextarea');
const answerTextarea = document.getElementById('answerTextarea');

let peer;

// Get user media
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
  .then(stream => {
    // Display local video stream
    playLocalButton.addEventListener('click', ()=>{
      localVideo.srcObject = stream;
      localVideo.muted = true;
      localVideo.play();
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
      playRemoteButton.addEventListener('click', ()=>{
        remoteVideo.srcObject = remoteStream;
        remoteVideo.muted = true;
        remoteVideo.play();
      })
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
