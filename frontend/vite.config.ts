/// <reference types="vitest/config" />

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
	base: "/srs-tour/",

	plugins: [react(), tailwindcss()],

	test: {
		environment: "jsdom",
		setupFiles: "./tests/setup/vitest.ts",
		exclude: ["tests/e2e/**", "node_modules/**"],
	},
});
