import { useState, useCallback, useRef, useEffect } from "react";
import {
	TranscriptionWebSocket,
	AudioRecorder,
	TranscriptionMessage,
} from "../websocket";
import { speechAPI, TranscriptionResult } from "../api";

export interface SpeechToTextState {
	isListening: boolean;
	isConnecting: boolean;
	transcription: string;
	confidence: number;
	error: string | null;
	audioLevel: number;
	sessionId: string | null;
}

export interface SpeechToTextActions {
	startListening: () => Promise<void>;
	stopListening: () => void;
	uploadAudioFile: (
		file: File,
		language?: string
	) => Promise<TranscriptionResult>;
	clearTranscription: () => void;
}

export function useSpeechToText(
	language: string = "vi-VN"
): [SpeechToTextState, SpeechToTextActions] {
	const [state, setState] = useState<SpeechToTextState>({
		isListening: false,
		isConnecting: false,
		transcription: "",
		confidence: 0,
		error: null,
		audioLevel: 0,
		sessionId: null,
	});

	const wsRef = useRef<TranscriptionWebSocket | null>(null);
	const recorderRef = useRef<AudioRecorder | null>(null);
	const audioLevelIntervalRef = useRef<NodeJS.Timeout | null>(null);

	// Handle WebSocket messages
	const handleWebSocketMessage = useCallback(
		(message: TranscriptionMessage) => {
			switch (message.type) {
				case "session_started":
					setState((prev) => ({
						...prev,
						sessionId: message.session_id || null,
						isConnecting: false,
						isListening: true,
						error: null,
					}));
					break;

				case "transcription":
					setState((prev) => ({
						...prev,
						transcription: message.text || "",
						confidence: message.confidence || 0,
						error: null,
					}));
					break;

				case "error":
					setState((prev) => ({
						...prev,
						error: message.message || "Lỗi không xác định",
						isConnecting: false,
						isListening: false,
					}));
					break;

				case "session_ended":
					setState((prev) => ({
						...prev,
						isListening: false,
						sessionId: null,
					}));
					break;
			}
		},
		[]
	);

	// Handle WebSocket errors
	const handleWebSocketError = useCallback((error: Event) => {
		setState((prev) => ({
			...prev,
			error: "Lỗi kết nối WebSocket",
			isConnecting: false,
			isListening: false,
		}));
	}, []);

	// Handle WebSocket close
	const handleWebSocketClose = useCallback(() => {
		setState((prev) => ({
			...prev,
			isListening: false,
			isConnecting: false,
		}));
	}, []);

	// Handle audio data from recorder
	const handleAudioData = useCallback((audioBlob: Blob) => {
		if (wsRef.current && wsRef.current.isConnected()) {
			// Convert blob to ArrayBuffer and send
			audioBlob.arrayBuffer().then((buffer) => {
				wsRef.current?.sendAudioData(buffer);
			});
		}
	}, []);

	// Handle recorder errors
	const handleRecorderError = useCallback((error: string) => {
		setState((prev) => ({
			...prev,
			error: error,
			isListening: false,
			isConnecting: false,
		}));
	}, []);

	// Start listening (real-time)
	const startListening = useCallback(async () => {
		try {
			setState((prev) => ({
				...prev,
				isConnecting: true,
				error: null,
				transcription: "",
				confidence: 0,
			}));

			// Initialize WebSocket
			wsRef.current = new TranscriptionWebSocket(
				handleWebSocketMessage,
				handleWebSocketError,
				handleWebSocketClose
			);

			// Connect WebSocket
			await wsRef.current.connect({ language });

			// Initialize audio recorder
			recorderRef.current = new AudioRecorder(
				handleAudioData,
				handleRecorderError
			);

			// Start recording
			await recorderRef.current.startRecording();

			// Start audio level monitoring
			audioLevelIntervalRef.current = setInterval(async () => {
				if (recorderRef.current) {
					const level = await recorderRef.current.getAudioLevel();
					setState((prev) => ({ ...prev, audioLevel: level }));
				}
			}, 100);
		} catch (error) {
			setState((prev) => ({
				...prev,
				error: `Lỗi khởi động: ${error}`,
				isConnecting: false,
				isListening: false,
			}));
		}
	}, [
		language,
		handleWebSocketMessage,
		handleWebSocketError,
		handleWebSocketClose,
		handleAudioData,
		handleRecorderError,
	]);

	// Stop listening
	const stopListening = useCallback(() => {
		// Stop audio recorder
		if (recorderRef.current) {
			recorderRef.current.stopRecording();
			recorderRef.current = null;
		}

		// Disconnect WebSocket
		if (wsRef.current) {
			wsRef.current.disconnect();
			wsRef.current = null;
		}

		// Clear audio level monitoring
		if (audioLevelIntervalRef.current) {
			clearInterval(audioLevelIntervalRef.current);
			audioLevelIntervalRef.current = null;
		}

		setState((prev) => ({
			...prev,
			isListening: false,
			isConnecting: false,
			audioLevel: 0,
			sessionId: null,
		}));
	}, []);

	// Upload audio file
	const uploadAudioFile = useCallback(
		async (
			file: File,
			lang: string = language
		): Promise<TranscriptionResult> => {
			try {
				setState((prev) => ({ ...prev, error: null }));

				const result = await speechAPI.uploadAudio(file, lang);

				setState((prev) => ({
					...prev,
					transcription: result.transcription,
					confidence: result.confidence,
				}));

				return result;
			} catch (error) {
				const errorMessage = `Lỗi upload file: ${error}`;
				setState((prev) => ({ ...prev, error: errorMessage }));
				throw new Error(errorMessage);
			}
		},
		[language]
	);

	// Clear transcription
	const clearTranscription = useCallback(() => {
		setState((prev) => ({
			...prev,
			transcription: "",
			confidence: 0,
			error: null,
		}));
	}, []);

	// Cleanup on unmount
	useEffect(() => {
		return () => {
			stopListening();
		};
	}, [stopListening]);

	return [
		state,
		{
			startListening,
			stopListening,
			uploadAudioFile,
			clearTranscription,
		},
	];
}
