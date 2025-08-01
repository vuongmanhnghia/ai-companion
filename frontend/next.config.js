/** @type {import('next').NextConfig} */
const nextConfig = {
	// Disable hydration warnings for development
	onDemandEntries: {
		// period (in ms) where the server will keep pages in the buffer
		maxInactiveAge: 25 * 1000,
		// number of pages that should be kept simultaneously without being disposed
		pagesBufferLength: 2,
	},
	// Suppress hydration warnings
	compiler: {
		// Remove console.logs in production
		removeConsole: process.env.NODE_ENV === "production",
	},
	async rewrites() {
		return [
			{
				source: "/api/:path*",
				destination: "http://localhost:8000/api/:path*",
			},
		];
	},
};

module.exports = nextConfig;
