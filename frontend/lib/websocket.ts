export interface TranscriptionMessage {
	type: "session_started" | "transcription" | "error" | "session_ended";
	session_id?: string;
	language?: string;
	message?: string;
	text?: string;
	confidence?: number;
	is_final?: boolean;
	timestamp?: string;
}

export interface WebSocketConfig {
	language: string;
	participants?: string[];
}

export class TranscriptionWebSocket {
	private ws: WebSocket | null = null;
	private url: string;
	private onMessage: (message: TranscriptionMessage) => void;
	private onError: (error: Event) => void;
	private onClose: () => void;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;

	constructor(
		onMessage: (message: TranscriptionMessage) => void,
		onError: (error: Event) => void = () => {},
		onClose: () => void = () => {}
	) {
		this.url =
			process.env.NODE_ENV === "production"
				? "wss://your-backend-url.com/api/transcription/live"
				: "ws://localhost:8000/api/transcription/live";

		this.onMessage = onMessage;
		this.onError = onError;
		this.onClose = onClose;
	}

	connect(config: WebSocketConfig): Promise<void> {
		return new Promise((resolve, reject) => {
			try {
				this.ws = new WebSocket(this.url);

				this.ws.onopen = () => {
					console.log("WebSocket connected");
					this.reconnectAttempts = 0;

					// Send configuration
					this.send(config);
					resolve();
				};

				this.ws.onmessage = (event) => {
					try {
						const message: TranscriptionMessage = JSON.parse(
							event.data
						);
						this.onMessage(message);
					} catch (error) {
						console.error(
							"Error parsing WebSocket message:",
							error
						);
					}
				};

				this.ws.onerror = (error) => {
					console.error("WebSocket error:", error);
					this.onError(error);
					reject(error);
				};

				this.ws.onclose = () => {
					console.log("WebSocket closed");
					this.onClose();
					this.handleReconnect(config);
				};
			} catch (error) {
				reject(error);
			}
		});
	}

	private handleReconnect(config: WebSocketConfig) {
		if (this.reconnectAttempts < this.maxReconnectAttempts) {
			this.reconnectAttempts++;
			console.log(
				`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
			);

			setTimeout(() => {
				this.connect(config);
			}, this.reconnectDelay * this.reconnectAttempts);
		} else {
			console.error("Max reconnection attempts reached");
		}
	}

	send(data: any) {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			if (typeof data === "string") {
				this.ws.send(data);
			} else {
				this.ws.send(JSON.stringify(data));
			}
		} else {
			console.warn("WebSocket is not connected");
		}
	}

	sendAudioData(audioData: ArrayBuffer) {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			this.ws.send(audioData);
		}
	}

	disconnect() {
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
	}

	isConnected(): boolean {
		return this.ws?.readyState === WebSocket.OPEN;
	}
}

// Audio Recording Class
export class AudioRecorder {
	private mediaRecorder: MediaRecorder | null = null;
	private audioStream: MediaStream | null = null;
	private onDataAvailable: (data: Blob) => void;
	private onError: (error: string) => void;

	constructor(
		onDataAvailable: (data: Blob) => void,
		onError: (error: string) => void = () => {}
	) {
		this.onDataAvailable = onDataAvailable;
		this.onError = onError;
	}

	async startRecording(): Promise<void> {
		try {
			// Request microphone access
			this.audioStream = await navigator.mediaDevices.getUserMedia({
				audio: {
					sampleRate: 16000,
					channelCount: 1,
					echoCancellation: true,
					noiseSuppression: true,
				},
			});

			// Create MediaRecorder
			this.mediaRecorder = new MediaRecorder(this.audioStream, {
				mimeType: "audio/webm;codecs=opus",
			});

			// Handle data available
			this.mediaRecorder.ondataavailable = (event) => {
				if (event.data.size > 0) {
					this.onDataAvailable(event.data);
				}
			};

			this.mediaRecorder.onerror = (event) => {
				this.onError("MediaRecorder error: " + event.error);
			};

			// Start recording with time slices
			this.mediaRecorder.start(1000); // Send data every 1 second
		} catch (error) {
			this.onError("Failed to start recording: " + error);
			throw error;
		}
	}

	stopRecording() {
		if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
			this.mediaRecorder.stop();
		}

		if (this.audioStream) {
			this.audioStream.getTracks().forEach((track) => track.stop());
			this.audioStream = null;
		}

		this.mediaRecorder = null;
	}

	isRecording(): boolean {
		return this.mediaRecorder?.state === "recording";
	}

	// Get audio level for visualization
	getAudioLevel(): Promise<number> {
		return new Promise((resolve) => {
			if (!this.audioStream) {
				resolve(0);
				return;
			}

			const audioContext = new AudioContext();
			const analyser = audioContext.createAnalyser();
			const microphone = audioContext.createMediaStreamSource(
				this.audioStream
			);

			analyser.fftSize = 256;
			const bufferLength = analyser.frequencyBinCount;
			const dataArray = new Uint8Array(bufferLength);

			microphone.connect(analyser);

			analyser.getByteFrequencyData(dataArray);

			// Calculate average volume
			let sum = 0;
			for (let i = 0; i < bufferLength; i++) {
				sum += dataArray[i];
			}
			const average = sum / bufferLength;

			resolve(Math.min(100, (average / 128) * 100));
		});
	}
}
