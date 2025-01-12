class VideoChat {
    constructor(room_id) {
        this.room_id = room_id;
        this.localStream = null;
        this.localPeer = null;
        this.remotePeer = null;
        this.socket = io.connect(); // Connect to the server
    }

    async initialize() {
        const room_id = this.room_id;
        if (!room_id) {
            console.error('Room ID is not defined');
            return;
        }

        this.localStream = await this.setupLocalMedia();

        // Create the peer connections
        this.localPeer = new SimplePeer({
            initiator: true,  // Initiator sets up the offer
            trickle: false,  // Disable trickling ICE candidates
            stream: this.localStream
        });

        this.remotePeer = new SimplePeer({
            initiator: false,  // Remote peer will respond to the offer
            trickle: false
        });

        // Handle signaling
        this.localPeer.on('signal', data => {
            this.socket.emit('offer', { room_id, offer: data });
        });

        this.remotePeer.on('signal', data => {
            this.socket.emit('answer', { room_id, answer: data });
        });

        this.localPeer.on('stream', stream => {
            document.getElementById('localVideo').srcObject = stream;  // This should be your local stream
          });
          
          this.remotePeer.on('stream', stream => {
            document.getElementById('remoteVideo').srcObject = stream;  // This should be the remote peer's stream
          });
          

        // Handle ICE candidates
        this.localPeer.on('icecandidate', candidate => {
            this.socket.emit('ice-candidate', { room_id, candidate });
        });

        this.remotePeer.on('icecandidate', candidate => {
            this.socket.emit('ice-candidate', { room_id, candidate });
        });

        // Join the room
        this.socket.emit('join', { room_id });

        // Handle server responses
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
