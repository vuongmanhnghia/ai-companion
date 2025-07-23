"use client";

import React, { useState, useEffect, useRef } from "react";
import {
	Mic,
	MicOff,
	Upload,
	Volume2,
	Settings,
	Activity,
	AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useSpeechToText } from "@/lib/hooks/useSpeechToText";
import { audioClassifierAPI, alertsAPI } from "@/lib/api";

interface TranscriptionData {
	text: string;
	confidence: number;
	timestamp: string;
	isListening: boolean;
}

interface AudioClassification {
	class: string;
	confidence: number;
}

interface AlertData {
	id: string;
	type: string;
	message: string;
	priority: "critical" | "high" | "medium" | "low";
	timestamp: string;
}

export default function Dashboard() {
	const [isClient, setIsClient] = useState(false);
	const fileInputRef = useRef<HTMLInputElement>(null);

	// Real Speech-to-Text hook
	const [speechState, speechActions] = useSpeechToText("vi-VN");

	// Use real speech state
	const isListening = speechState.isListening;
	const isConnecting = speechState.isConnecting;
	const audioLevel = speechState.audioLevel;
	const error = speechState.error;

	const [transcription, setTranscription] = useState<TranscriptionData>({
		text: "Chào mừng bạn đến với AI Companion. Nhấn nút microphone để bắt đầu hoặc upload file âm thanh.",
		confidence: 0,
		timestamp: "",
		isListening: false,
	});

	const [audioClassifications, setAudioClassifications] = useState<
		AudioClassification[]
	>([
		{ class: "Speech", confidence: 0.85 },
		{ class: "Conversation", confidence: 0.72 },
		{ class: "Background noise", confidence: 0.45 },
	]);

	const [alerts, setAlerts] = useState<AlertData[]>([
		{
			id: "1",
			type: "doorbell",
			message: "Phát hiện tiếng chuông cửa",
			priority: "medium",
			timestamp: "",
		},
	]);

	// Update transcription from speech state
	useEffect(() => {
		if (speechState.transcription) {
			setTranscription((prev) => ({
				...prev,
				text: speechState.transcription,
				confidence: speechState.confidence,
				timestamp: new Date().toISOString(),
				isListening: speechState.isListening,
			}));
		}
	}, [
		speechState.transcription,
		speechState.confidence,
		speechState.isListening,
	]);

	// Fix hydration issue
	useEffect(() => {
		setIsClient(true);
		const now = new Date().toISOString();

		setTranscription((prev) => ({
			...prev,
			timestamp: now,
		}));

		setAlerts((prev) =>
			prev.map((alert) => ({
				...alert,
				timestamp: now,
			}))
		);
	}, []);

	// Real toggle listening function
	const toggleListening = async () => {
		try {
			if (!isListening && !isConnecting) {
				await speechActions.startListening();
			} else {
				speechActions.stopListening();
			}
		} catch (err) {
			console.error("Error toggling listening:", err);
		}
	};

	// Handle file upload
	const handleFileUpload = async (
		event: React.ChangeEvent<HTMLInputElement>
	) => {
		const file = event.target.files?.[0];
		if (!file) return;

		try {
			const result = await speechActions.uploadAudioFile(file);
			console.log("Upload result:", result);
		} catch (err) {
			console.error("Upload error:", err);
		}

		// Reset file input
		if (fileInputRef.current) {
			fileInputRef.current.value = "";
		}
	};

	// Clear transcription
	const clearTranscription = () => {
		speechActions.clearTranscription();
		setTranscription({
			text: "Chào mừng bạn đến với AI Companion. Nhấn nút microphone để bắt đầu hoặc upload file âm thanh.",
			confidence: 0,
			timestamp: "",
			isListening: false,
		});
	};

	const getPriorityColor = (priority: string) => {
		switch (priority) {
			case "critical":
				return "bg-red-100 text-red-800 border-red-200";
			case "high":
				return "bg-orange-100 text-orange-800 border-orange-200";
			case "medium":
				return "bg-yellow-100 text-yellow-800 border-yellow-200";
			case "low":
				return "bg-blue-100 text-blue-800 border-blue-200";
			default:
				return "bg-gray-100 text-gray-800 border-gray-200";
		}
	};

	const formatTime = (timestamp: string) => {
		if (!isClient || !timestamp) return "";
		return new Date(timestamp).toLocaleTimeString("vi-VN");
	};

	const formatDateTime = (timestamp: string) => {
		if (!isClient || !timestamp) return "";
		return new Date(timestamp).toLocaleString("vi-VN");
	};

	// Loading state during hydration
	if (!isClient) {
		return (
			<div className="p-4 min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
				<div className="mx-auto max-w-7xl">
					<div className="mb-8">
						<h1 className="mb-2 text-4xl font-bold text-gray-900">
							🎧 AI Companion
						</h1>
						<p className="text-xl text-gray-600">
							Hỗ trợ người khiếm thính với AI thông minh
						</p>
					</div>
					<div className="flex justify-center items-center h-64">
						<div className="text-center">
							<div className="mx-auto mb-4 w-12 h-12 rounded-full border-b-2 border-blue-600 animate-spin"></div>
							<p className="text-gray-600">
								Đang tải hệ thống...
							</p>
						</div>
					</div>
				</div>
			</div>
		);
	}

	return (
		<div className="p-4 min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
			<div className="mx-auto max-w-7xl">
				{/* Header */}
				<div className="mb-8">
					<h1 className="mb-2 text-4xl font-bold text-gray-900">
						🎧 AI Companion
					</h1>
					<p className="text-xl text-gray-600">
						Hỗ trợ người khiếm thính với AI thông minh
					</p>
				</div>

				{/* Error Alert */}
				{error && (
					<Alert className="mb-6 bg-red-50 border-red-200">
						<AlertCircle className="w-4 h-4" />
						<AlertDescription className="text-red-800">
							{error}
							<Button
								variant="ghost"
								size="sm"
								onClick={() =>
									speechActions.clearTranscription()
								}
								className="px-2 ml-2 h-6 text-red-600 hover:text-red-800">
								✕
							</Button>
						</AlertDescription>
					</Alert>
				)}

				{/* Main Dashboard */}
				<div className="grid grid-cols-1 gap-6 mb-8 lg:grid-cols-3">
					{/* Speech-to-Text Panel */}
					<div className="lg:col-span-2">
						<Card className="h-full">
							<CardHeader>
								<div className="flex justify-between items-center">
									<div>
										<CardTitle className="flex gap-2 items-center">
											<Mic className="w-5 h-5" />
											Chuyển đổi Lời nói
										</CardTitle>
										<CardDescription>
											Google Cloud Speech-to-Text - Độ
											chính xác 99%
										</CardDescription>
									</div>
									<div className="flex gap-2">
										{/* Upload Button */}
										<Button
											variant="outline"
											size="lg"
											onClick={() =>
												fileInputRef.current?.click()
											}
											className="flex gap-2 items-center">
											<Upload className="w-4 h-4" />
											Upload
										</Button>

										{/* Record Button */}
										<Button
											onClick={toggleListening}
											variant={
												isListening
													? "destructive"
													: "default"
											}
											size="lg"
											disabled={isConnecting}
											className="flex gap-2 items-center">
											{isConnecting ? (
												<>
													<div className="w-4 h-4 rounded-full border-b-2 border-white animate-spin"></div>
													Kết nối...
												</>
											) : isListening ? (
												<>
													<MicOff className="w-4 h-4" />
													Dừng
												</>
											) : (
												<>
													<Mic className="w-4 h-4" />
													Bắt đầu
												</>
											)}
										</Button>
									</div>
								</div>
							</CardHeader>
							<CardContent className="space-y-4">
								{/* Audio Level Indicator */}
								<div className="space-y-2">
									<div className="flex justify-between items-center text-sm">
										<span>Mức âm thanh</span>
										<span>{Math.round(audioLevel)}%</span>
									</div>
									<Progress
										value={audioLevel}
										className="h-2"
									/>
								</div>

								{/* Transcription Display */}
								<div className="bg-gray-50 rounded-lg p-6 min-h-[200px]">
									<div className="flex gap-3 items-start">
										<div
											className={`w-3 h-3 rounded-full mt-2 ${
												isListening
													? "bg-green-500 animate-pulse"
													: isConnecting
													? "bg-yellow-500 animate-pulse"
													: "bg-gray-400"
											}`}
										/>
										<div className="flex-1">
											<p className="text-lg leading-relaxed text-gray-800">
												{transcription.text}
											</p>
											{transcription.confidence > 0 && (
												<div className="flex gap-2 items-center mt-3 text-sm text-gray-600">
													<Badge variant="secondary">
														Độ tin cậy:{" "}
														{Math.round(
															transcription.confidence *
																100
														)}
														%
													</Badge>
													<span>
														{formatTime(
															transcription.timestamp
														)}
													</span>
												</div>
											)}
											{transcription.text && (
												<Button
													variant="ghost"
													size="sm"
													onClick={clearTranscription}
													className="mt-2 text-gray-500 hover:text-gray-700">
													Xóa văn bản
												</Button>
											)}
										</div>
									</div>
								</div>

								{/* Hidden file input */}
								<input
									ref={fileInputRef}
									type="file"
									accept="audio/*"
									onChange={handleFileUpload}
									className="hidden"
								/>
							</CardContent>
						</Card>
					</div>

					{/* Audio Classification Panel */}
					<div>
						<Card className="h-full">
							<CardHeader>
								<CardTitle className="flex gap-2 items-center">
									<Volume2 className="w-5 h-5" />
									Phân loại Âm thanh
								</CardTitle>
								<CardDescription>
									YAMNet - 521 loại âm thanh
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="space-y-3">
									{audioClassifications.map((item, index) => (
										<div
											key={index}
											className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
											<div>
												<p className="text-sm font-medium">
													{item.class}
												</p>
												<Progress
													value={
														item.confidence * 100
													}
													className="mt-1 w-24 h-1"
												/>
											</div>
											<Badge variant="outline">
												{Math.round(
													item.confidence * 100
												)}
												%
											</Badge>
										</div>
									))}
								</div>
							</CardContent>
						</Card>
					</div>
				</div>

				{/* Tabs Section */}
				<Tabs defaultValue="alerts" className="space-y-6">
					<TabsList className="grid grid-cols-4 w-full">
						<TabsTrigger value="alerts">Cảnh báo</TabsTrigger>
						<TabsTrigger value="transcription">
							Phiên ghi âm
						</TabsTrigger>
						<TabsTrigger value="statistics">Thống kê</TabsTrigger>
						<TabsTrigger value="settings">Cài đặt</TabsTrigger>
					</TabsList>

					{/* Alerts Tab */}
					<TabsContent value="alerts">
						<Card>
							<CardHeader>
								<CardTitle>Cảnh báo Âm thanh</CardTitle>
								<CardDescription>
									Phát hiện các âm thanh quan trọng cần chú ý
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ScrollArea className="h-[300px]">
									<div className="space-y-3">
										{alerts.map((alert) => (
											<Alert
												key={alert.id}
												className={getPriorityColor(
													alert.priority
												)}>
												<Activity className="w-4 h-4" />
												<AlertDescription className="flex justify-between items-center">
													<div>
														<p className="font-medium">
															{alert.message}
														</p>
														<p className="text-xs opacity-70">
															{formatDateTime(
																alert.timestamp
															)}
														</p>
													</div>
													<Badge
														variant="outline"
														className="ml-2">
														{alert.priority}
													</Badge>
												</AlertDescription>
											</Alert>
										))}
									</div>
								</ScrollArea>
							</CardContent>
						</Card>
					</TabsContent>

					{/* Transcription Tab */}
					<TabsContent value="transcription">
						<Card>
							<CardHeader>
								<CardTitle>Phiên Transcription</CardTitle>
								<CardDescription>
									Quản lý các phiên chuyển đổi lời nói thành
									văn bản
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="py-12 text-center text-gray-500">
									<Mic className="mx-auto mb-4 w-12 h-12 opacity-50" />
									<p>Chưa có phiên transcription nào</p>
									<p className="text-sm">
										Nhấn "Bắt đầu" để tạo phiên mới
									</p>
								</div>
							</CardContent>
						</Card>
					</TabsContent>

					{/* Statistics Tab */}
					<TabsContent value="statistics">
						<Card>
							<CardHeader>
								<CardTitle>Thống kê Sử dụng</CardTitle>
								<CardDescription>
									Báo cáo hoạt động hệ thống
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="grid grid-cols-1 gap-4 md:grid-cols-3">
									<div className="p-4 text-center bg-blue-50 rounded-lg">
										<div className="text-2xl font-bold text-blue-600">
											15
										</div>
										<div className="text-sm text-blue-600">
											Phiên hôm nay
										</div>
									</div>
									<div className="p-4 text-center bg-green-50 rounded-lg">
										<div className="text-2xl font-bold text-green-600">
											98%
										</div>
										<div className="text-sm text-green-600">
											Độ chính xác
										</div>
									</div>
									<div className="p-4 text-center bg-purple-50 rounded-lg">
										<div className="text-2xl font-bold text-purple-600">
											3
										</div>
										<div className="text-sm text-purple-600">
											Cảnh báo
										</div>
									</div>
								</div>
							</CardContent>
						</Card>
					</TabsContent>

					{/* Settings Tab */}
					<TabsContent value="settings">
						<Card>
							<CardHeader>
								<CardTitle>Cài đặt Hệ thống</CardTitle>
								<CardDescription>
									Tùy chỉnh các thông số hoạt động
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="space-y-6">
									<div>
										<h3 className="mb-3 text-lg font-medium">
											Ngôn ngữ
										</h3>
										<Badge variant="secondary">
											Tiếng Việt (vi-VN)
										</Badge>
									</div>

									<Separator />

									<div>
										<h3 className="mb-3 text-lg font-medium">
											Cảnh báo Âm thanh
										</h3>
										<div className="space-y-2">
											<div className="flex justify-between items-center p-2 bg-gray-50 rounded">
												<span>Báo cháy</span>
												<Badge className="text-red-800 bg-red-100">
													Bật
												</Badge>
											</div>
											<div className="flex justify-between items-center p-2 bg-gray-50 rounded">
												<span>Chuông cửa</span>
												<Badge className="text-green-800 bg-green-100">
													Bật
												</Badge>
											</div>
											<div className="flex justify-between items-center p-2 bg-gray-50 rounded">
												<span>Tiếng khóc trẻ em</span>
												<Badge className="text-green-800 bg-green-100">
													Bật
												</Badge>
											</div>
										</div>
									</div>
								</div>
							</CardContent>
						</Card>
					</TabsContent>
				</Tabs>
			</div>
		</div>
	);
}
