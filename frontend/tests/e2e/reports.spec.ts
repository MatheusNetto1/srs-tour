import { expect, test } from "@playwright/test";

test.describe("Reports page", () => {
	test("displays the public reports page", async ({ page }) => {
		await page.goto("/#/relatorios");

		await expect(
			page.getByRole("heading", {
				level: 1,
				name: /relatórios e pesquisas/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: /publicações disponíveis/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("searchbox", {
				name: /buscar relatório/i,
			}),
		).toBeVisible();

		await expect(
			page.getByRole("combobox", {
				name: /ano/i,
			}),
		).toBeVisible();
	});

	test("filters reports by search term", async ({ page }) => {
		await page.goto("/#/relatorios");

		await page
			.getByRole("searchbox", {
				name: /buscar relatório/i,
			})
			.fill("Perfil");

		await expect(
			page.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2026",
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2025",
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: "Relatório Anual do Turismo 2026",
			}),
		).not.toBeVisible();

		await expect(page.getByText(/2 publicações encontradas/i)).toBeVisible();
	});

	test("filters reports by year", async ({ page }) => {
		await page.goto("/#/relatorios");

		await page
			.getByRole("combobox", {
				name: /ano/i,
			})
			.selectOption("2025");

		await expect(
			page.getByRole("heading", {
				name: "Relatório Anual do Turismo 2025",
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2025",
			}),
		).toBeVisible();

		await expect(
			page.getByRole("heading", {
				name: "Relatório Anual do Turismo 2026",
			}),
		).not.toBeVisible();

		await expect(page.getByText(/2 publicações encontradas/i)).toBeVisible();
	});

	test("shows an empty state when no report matches", async ({ page }) => {
		await page.goto("/#/relatorios");

		await page
			.getByRole("searchbox", {
				name: /buscar relatório/i,
			})
			.fill("relatório que não existe");

		await expect(
			page.getByRole("heading", {
				name: /nenhuma publicação encontrada/i,
			}),
		).toBeVisible();

		await expect(page.getByText(/0 publicações encontradas/i)).toBeVisible();
	});
});
