import { expect, test } from "@playwright/test";

test.describe("Indicators page", () => {
	test("displays the public indicators dashboard", async ({ page }) => {
		await page.goto("/#/indicadores");

		await expect(
			page.getByRole("heading", {
				level: 1,
				name: /indicadores turísticos/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: /evolução dos estabelecimentos/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: /distribuição por setor/i,
			}),
		).toBeVisible();
	});

	test("filters indicators by sector", async ({ page }) => {
		await page.goto("/#/indicadores");

		await page
			.getByRole("combobox", {
				name: /setor/i,
			})
			.selectOption("Alimentação");

		await expect(
			page.getByText("Estabelecimentos de alimentação"),
		).toBeVisible();

		await expect(
			page.getByText("Empresas de serviços turísticos"),
		).not.toBeVisible();
	});

	test("filters indicators by period", async ({ page }) => {
		await page.goto("/#/indicadores");

		await page
			.getByRole("combobox", {
				name: /período/i,
			})
			.selectOption("2025");

		await expect(page.getByText(/estabelecimentos em 2025/i)).toBeVisible();
	});
});
