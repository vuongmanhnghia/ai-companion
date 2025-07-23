import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import React from "react";

const inter = Inter({ subsets: ["latin", "vietnamese"] });

export const metadata: Metadata = {
	title: "AI Companion - Hỗ trợ người khiếm thính",
	description:
		"Hệ thống AI hỗ trợ người khiếm thính với Speech-to-Text và Audio Classification",
};

export default function RootLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<html lang="vi" suppressHydrationWarning>
			<body className={`${inter.className} vietnamese-text`}>
				{children}
			</body>
		</html>
	);
}
