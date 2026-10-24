/// <reference types="vitest/config" />

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [react(), tailwindcss()],

	server: {
		// `/api` vai para o backend: o navegador fala só com a origem do Vite,
		// então não há CORS. No container o destino é http://backend:8000.
		proxy: {
			"/api": {
				target: process.env.API_PROXY_TARGET ?? "http://localhost:8000",
				changeOrigin: true,
			},
		},
		watch: {
			// Só no container (compose.yml): o bind mount do Windows não propaga
			// eventos de arquivo. No host (`make front-dev`) o padrão basta.
			usePolling: process.env.DEV_USE_POLLING === "true",
		},
	},

	test: {
		environment: "jsdom",
		setupFiles: "./tests/setup/vitest.ts",
		exclude: ["tests/e2e/**", "tests/visual/**", "node_modules/**"],
	},
});
