import axios from "axios";

// Base API URL
const API_BASE_URL =
	process.env.NODE_ENV === "production"
		? "https://your-backend-url.com"
		: "http://localhost:8000";

// Create axios instance
const apiClient = axios.create({
	baseURL: API_BASE_URL,
	timeout: 30000,
	headers: {
		"Content-Type": "application/json",
	},
});

// API Types
export interface TranscriptionResult {
	success: boolean;
	transcription: string;
	confidence: number;
	language: string;
	filename?: string;
}

export interface AudioClassificationResult {
	success: boolean;
	classifications: Array<{
		class: string;
		confidence: number;
	}>;
	top_prediction: {
		class: string;
		confidence: number;
	};
	filename?: string;
	model: string;
}

export interface ServiceStatus {
	service: string;
	status: "active" | "inactive" | "error";
	accuracy?: string;
	error?: string;
}

// API Functions
export const speechAPI = {
	// Upload audio file for transcription
	uploadAudio: async (
		file: File,
		language: string = "vi-VN"
	): Promise<TranscriptionResult> => {
		const formData = new FormData();
		formData.append("file", file);
		formData.append("language", language);

		const response = await apiClient.post("/api/speech/upload", formData, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
		});

		return response.data;
	},

	// Get supported languages
	getSupportedLanguages: async () => {
		const response = await apiClient.get("/api/speech/languages");
		return response.data;
	},

	// Check speech service status
	getStatus: async (): Promise<ServiceStatus> => {
		const response = await apiClient.get("/api/speech/status");
		return response.data;
	},
};

export const audioClassifierAPI = {
	// Classify audio file
	classifyAudio: async (
		file: File,
		topK: number = 5
	): Promise<AudioClassificationResult> => {
		const formData = new FormData();
		formData.append("file", file);

		const response = await apiClient.post(
			`/api/audio/classify?top_k=${topK}`,
			formData,
			{
				headers: {
					"Content-Type": "multipart/form-data",
				},
			}
		);

		return response.data;
	},

	// Get critical sounds list
	getCriticalSounds: async () => {
		const response = await apiClient.get("/api/audio/critical-sounds");
		return response.data;
	},

	// Check classifier service status
	getStatus: async (): Promise<ServiceStatus> => {
		const response = await apiClient.get("/api/audio/status");
		return response.data;
	},
};

export const transcriptionAPI = {
	// Start transcription session
	startSession: async (
		language: string = "vi-VN",
		participants: string[] = []
	) => {
		const response = await apiClient.post(
			"/api/transcription/session/start",
			{
				language,
				participants,
			}
		);
		return response.data;
	},

	// End transcription session
	endSession: async (sessionId: string) => {
		const response = await apiClient.post(
			`/api/transcription/session/${sessionId}/end`
		);
		return response.data;
	},

	// Get session transcript
	getSessionTranscript: async (sessionId: string) => {
		const response = await apiClient.get(
			`/api/transcription/session/${sessionId}/transcript`
		);
		return response.data;
	},

	// Get all sessions
	getSessions: async (limit: number = 20) => {
		const response = await apiClient.get(
			`/api/transcription/sessions?limit=${limit}`
		);
		return response.data;
	},
};

export const alertsAPI = {
	// Get alert settings
	getSettings: async () => {
		const response = await apiClient.get("/api/alerts/settings");
		return response.data;
	},

	// Get alert history
	getHistory: async (limit: number = 50, soundType?: string) => {
		const params = new URLSearchParams({ limit: limit.toString() });
		if (soundType) params.append("sound_type", soundType);

		const response = await apiClient.get(`/api/alerts/history?${params}`);
		return response.data;
	},

	// Test alert system
	testSystem: async () => {
		const response = await apiClient.post("/api/alerts/test");
		return response.data;
	},
};

export default apiClient;
