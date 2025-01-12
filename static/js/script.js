class VideoChat {
    constructor(room_id) {
        this.room_id = room_id;
        this.localStream = null;
        this.localPeer = null;
        this.remotePeer = null;
        this.socket = io.connect({ transports: ['websocket'] }); // Connect to the server
        this.localVideo = document.getElementById('localVideo');
        this.remoteVideo = document.getElementById('remoteVideo');
        this.offerTextarea = document.getElementById('offerTextarea');
        this.answerTextarea = document.getElementById('answerTextarea');
        this.connectButton = document.getElementById('connectButton');
    }

    async initialize() {
        const room_id = this.room_id;
        if (!room_id) {
            console.error('Room ID is not defined');
            return;
        }

        this.localStream = await this.setupLocalMedia();
        
        // Initialize local peer
        this.localPeer = new SimplePeer({
            initiator: true,  // Initiator sets up the offer
            trickle: false,   // Disable trickling ICE candidates
            stream: this.localStream
        });

        // Initialize remote peer (waiting for offer)
        this.remotePeer = new SimplePeer({
            initiator: false,  // Remote peer will respond to the offer
            trickle: false
        });

        // Handle signaling for local and remote peers
        this.localPeer.on('signal', data => {
            const signalString = JSON.stringify(data);
            this.offerTextarea.value = signalString;  // Show offer
            this.socket.emit('offer', { room_id, offer: data });
        });

        this.remotePeer.on('signal', data => {
            const signalString = JSON.stringify(data);
            this.answerTextarea.value = signalString;  // Show answer
            this.socket.emit('answer', { room_id, answer: data });
        });

        // Display local stream in the video element
        this.localPeer.on('stream', stream => {
            this.localVideo.srcObject = stream;
            this.localVideo.muted = true;  // Mute local video
            this.localVideo.play();
        });

        // Display remote stream when received
        this.remotePeer.on('stream', stream => {
            this.remoteVideo.srcObject = stream;
            this.remoteVideo.muted = true;  // Mute remote video
            this.remoteVideo.play();
        });

        // Handle ICE candidates for connection
        this.localPeer.on('icecandidate', candidate => {
            this.socket.emit('ice-candidate', { room_id, candidate });
        });

        this.remotePeer.on('icecandidate', candidate => {
            this.socket.emit('ice-candidate', { room_id, candidate });
        });

        // Join the room
        this.socket.emit('join', { room_id });

        // Handle server signaling messages
        this.socket.on('offer', data => {
            if (this.localPeer) {
                this.remotePeer.signal(data.offer);
            }
        });

        this.socket.on('answer', data => {
            if (this.localPeer) {
                this.localPeer.signal(data.answer);
            }
        });

        this.socket.on('ice-candidate', data => {
            if (data.candidate) {
                this.remotePeer.addIceCandidate(new RTCIceCandidate(data.candidate));
            }
        });

        // Handle connect button click for peer connection
        this.connectButton.addEventListener('click', () => {
            const signalData = this.localPeer.initiator ? this.answerTextarea.value : this.offerTextarea.value;
            try {
                this.localPeer.signal(JSON.parse(signalData));
            } catch (err) {
                console.error('Invalid signal data:', err);
            }
        });
    }

    async setupLocalMedia() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            return stream;
        } catch (err) {
            console.error('Error accessing media devices:', err);
            throw new Error('Unable to access camera or microphone');
        }
    }

    cleanup() {
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }

        if (this.localPeer) {
            this.localPeer.destroy();
        }

        if (this.remotePeer) {
            this.remotePeer.destroy();
        }
    }
}

