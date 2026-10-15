import process from "node:process";
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
	testDir: "./tests/visual",
	snapshotPathTemplate: "{testDir}/__screenshots__/{arg}{ext}",
	expect: {
		toHaveScreenshot: { animations: "disabled", maxDiffPixelRatio: 0.001 },
	},
	use: {
		baseURL: process.env.VISUAL_BASE_URL ?? "http://localhost:5173",
		// @ts-expect-error
		reducedMotion: "reduce",
	},
	projects: [
		{
			name: "chromium",
			use: { ...devices["Desktop Chrome"] },
		},
	],
	webServer: process.env.VISUAL_BASE_URL
		? undefined
		: {
				command: "npm run dev",
				url: "http://localhost:5173",
				reuseExistingServer: true,
			},
});
