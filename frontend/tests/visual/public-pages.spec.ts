import { expect, test } from "@playwright/test";
import { routeUrl, waitForStablePage } from "./helpers";

const routes = [
	{ path: "/", name: "home" },
	{ path: "/indicadores", name: "indicadores" },
	{ path: "/relatorios", name: "relatorios" },
	{ path: "/sobre", name: "sobre" },
];

const viewports = [
	{ name: "1440x900", width: 1440, height: 900 },
	{ name: "768x1024", width: 768, height: 1024 },
	{ name: "390x844", width: 390, height: 844 },
];

for (const route of routes) {
	for (const vp of viewports) {
		test.use({ viewport: { width: vp.width, height: vp.height } });

		test(`Snapshot: ${route.name} (${vp.name})`, async ({ page }) => {
			await page.goto(routeUrl(route.path));
			await waitForStablePage(page);
			await expect(page).toHaveScreenshot(`${route.name}__${vp.name}.png`, {
				fullPage: true,
			});
		});
	}
}
