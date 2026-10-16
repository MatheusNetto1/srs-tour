import process from "node:process";
import type { Page } from "@playwright/test";

export function routeUrl(path: string): string {
	const mode = process.env.VISUAL_ROUTE_MODE || "path";
	return mode === "hash" ? `/#${path}` : path;
}

export async function waitForStablePage(page: Page) {
	await page.waitForLoadState("networkidle");
	await page.evaluate(() => document.fonts.ready);
	await page.waitForFunction(() =>
		[...document.images].every((img) => img.complete && img.naturalWidth > 0),
	);
	// Só espera os gráficos nas páginas que os têm (Indicadores).
	if ((await page.locator(".recharts-wrapper").count()) > 0) {
		await page.locator(".recharts-line-curve").first().waitFor();
		await page.locator(".recharts-bar-rectangle").first().waitFor();
	}
	await page.addStyleTag({
		content:
			"*,*::before,*::after{animation:none!important;transition:none!important}",
	});
	await page.waitForTimeout(800);
}
