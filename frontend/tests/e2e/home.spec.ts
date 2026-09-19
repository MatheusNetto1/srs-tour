import { expect, test } from "@playwright/test";

test.describe("Home page", () => {
	test("displays the main public content", async ({ page }) => {
		await page.goto("/#/");

		await expect(
			page.getByRole("heading", {
				level: 1,
				name: /dados para compreender e fortalecer o turismo/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("link", {
				name: /explorar indicadores/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("link", {
				name: /ver relatórios/i,
			}),
		).toBeVisible();
	});

	test("navigates to indicators", async ({ page }) => {
		await page.goto("/#/");

		await page
			.getByRole("link", {
				name: /explorar indicadores/i,
			})
			.click();

		await expect(page).toHaveURL(/#\/indicadores/);
	});
});
