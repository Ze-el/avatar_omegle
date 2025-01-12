const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const connectButton = document.getElementById('connectButton');
const offerTextarea = document.getElementById('offerTextarea');
const answerTextarea = document.getElementById('answerTextarea');
const localcanvas = document.getElementById('localcanvas');

// WebSocket setup
const socket = new WebSocket('wss://avatar-omegle-hni6.onrender.com/');

socket.onopen = function() {
  console.log('WebSocket connection established');
};

socket.onmessage = function(event) {
  const message = JSON.parse(event.data);
  const base64Image = message.frame;

  // Create an Image element to hold the base64-encoded image
  const img = new Image();
  img.src = 'data:image/jpeg;base64,' + base64Image;

  img.onload = function () {
    // Create a canvas to draw the image on
    const context = localcanvas.getContext('2d');

    // Draw the image on the canvas
    context.drawImage(img, 0, 0);

    // Optionally, you can add further processing to manipulate the canvas

    // Attach the processed frame to the local video element
    // const stream = canvas.captureStream(30);
    // localVideo.srcObject = stream; // Capture the canvas as a video stream
  };
};

// Handle WebRTC connection setup
let peer;

  // Initialize SimplePeer and handle signaling as usual
  peer = new SimplePeer({ initiator: location.hash === '#1', trickle: false });

  peer.on('signal', (data) => {
    const signalString = JSON.stringify(data);
    console.log("breakpoint1")
    if (peer.initiator) {
      console.log("initiator")
      offerTextarea.value = signalString; // Show offer
    } else {
      answerTextarea.value = signalString; // Show answer
    }
  });

  peer.on('stream', (remoteStream) => {
    remoteVideo.srcObject = remoteStream;
    remoteVideo.muted = true;
    remoteVideo.play();
  });

// Handle connection button click
connectButton.addEventListener('click', () => {
  const signalData = peer.initiator ? answerTextarea.value : offerTextarea.value;
  try {
    peer.signal(JSON.parse(signalData));
  } catch (err) {
    console.error('Invalid signal data:', err);
  }
});
