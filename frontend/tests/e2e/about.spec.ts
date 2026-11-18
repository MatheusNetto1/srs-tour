import { expect, test } from "@playwright/test";

test.describe("About page", () => {
	test("displays the institutional page", async ({ page }) => {
		await page.goto("/sobre");

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
		await page.goto("/sobre");

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

	test("shows the Cadastur and FNRH Digital section", async ({ page }) => {
		await page.goto("/sobre");

		const main = page.getByRole("main");

		await expect(
			main.getByRole("heading", { name: "Cadastur e FNRH Digital" }),
		).toBeVisible();

		const links = [
			{ name: /acessar o cadastur/i, href: "https://cadastur.turismo.gov.br" },
			{
				name: /acessar a fnrh digital/i,
				href: "https://fnrh.turismo.gov.br",
			},
		];

		// Só confere os atributos: o teste não navega para os sites externos.
		for (const { name, href } of links) {
			const link = main.getByRole("link", { name });

			await expect(link).toBeVisible();
			await expect(link).toHaveAttribute("href", href);
			await expect(link).toHaveAttribute("target", "_blank");
			await expect(link).toHaveAttribute("rel", "noopener noreferrer");
		}

		await expect(
			main.getByText(/o observatório não se integra ao cadastur/i),
		).toBeVisible();
	});

	test("shows the logos of the three institutional levels", async ({
		page,
	}) => {
		await page.goto("/sobre");

		const main = page.getByRole("main");

		for (const name of [
			/santa rita do sapucaí – cidade criativa, cidade feliz/i,
			/prefeitura municipal de santa rita do sapucaí/i,
			/circuito turístico caminhos da mantiqueira/i,
			/minas gerais/i,
		]) {
			const logo = main.getByRole("img", { name });

			await expect(logo).toBeVisible();
			expect(
				await logo.evaluate((img: HTMLImageElement) => img.naturalWidth),
			).toBeGreaterThan(0);
		}
	});
});
