import { expect, test } from "@playwright/test";

test.describe("About page", () => {
	test("displays the institutional page", async ({ page }) => {
		await page.goto("/#/sobre");

		await expect(
			page.getByRole("heading", {
				level: 1,
				name: /sobre o observatório/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: /informação para compreender o turismo local/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: /por que organizar essas informações/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: /o que é acompanhado/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: /para quem são essas informações/i,
			}),
		).toBeVisible();
	});

	test("shows the institutional identities", async ({ page }) => {
		await page.goto("/#/sobre");

		const main = page.getByRole("main");

		await expect(
			main.getByRole("img", {
				name: /observatório do turismo de santa rita do sapucaí/i,
			}),
		).toBeVisible();

		await expect(
			main.getByRole("img", {
				name: /secretaria municipal de cultura, esporte, lazer e turismo/i,
			}),
		).toBeVisible();

		await expect(
			main.getByRole("img", {
				name: /conselho municipal de turismo/i,
			}),
		).toBeVisible();
	});
});
