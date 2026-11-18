import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { About } from "../../../src/pages/About/About";

describe("About page", () => {
	it("renders the institutional content", () => {
		render(<About />);

		expect(
			screen.getByRole("heading", {
				level: 1,
				name: /sobre o observatório/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: /informação para compreender o turismo local/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByText(
				/o observatório do turismo de santa rita do sapucaí reúne e organiza informações/i,
			),
		).toBeInTheDocument();
	});

	it("explains the purpose of the platform", () => {
		render(<About />);

		expect(
			screen.getByRole("heading", {
				name: /por que organizar essas informações/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Centralizar",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Atualizar",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Democratizar",
			}),
		).toBeInTheDocument();
	});

	it("shows the information monitored by the observatory", () => {
		render(<About />);

		expect(
			screen.getByRole("heading", {
				name: /o que é acompanhado/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Meios de hospedagem",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Empresas e empregos",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Fluxo de visitantes",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Pesquisas e relatórios",
			}),
		).toBeInTheDocument();
	});

	it("shows the audiences of the platform", () => {
		render(<About />);

		expect(
			screen.getByRole("heading", {
				name: /para quem são essas informações/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Gestores públicos",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Empreendedores",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Pesquisadores",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "População",
			}),
		).toBeInTheDocument();
	});

	it("shows the institutional identities", () => {
		render(<About />);

		expect(
			screen.getByRole("img", {
				name: /observatório do turismo de santa rita do sapucaí/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("img", {
				name: /secretaria municipal de cultura, esporte, lazer e turismo/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("img", {
				name: /conselho municipal de turismo/i,
			}),
		).toBeInTheDocument();
	});

	it("shows the Cadastur and FNRH Digital guidance with official links", () => {
		render(<About />);

		expect(
			screen.getByRole("heading", {
				level: 2,
				name: "Cadastur e FNRH Digital",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", { level: 3, name: "Cadastur" }),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", { level: 3, name: "FNRH Digital" }),
		).toBeInTheDocument();

		const cadastur = screen.getByRole("link", { name: /acessar o cadastur/i });

		expect(cadastur).toHaveAttribute("href", "https://cadastur.turismo.gov.br");
		expect(cadastur).toHaveAttribute("target", "_blank");
		expect(cadastur).toHaveAttribute("rel", "noopener noreferrer");
		expect(cadastur).toHaveAccessibleName(/abre em nova aba/i);

		const fnrh = screen.getByRole("link", { name: /acessar a fnrh digital/i });

		expect(fnrh).toHaveAttribute("href", "https://fnrh.turismo.gov.br");
		expect(fnrh).toHaveAttribute("target", "_blank");
		expect(fnrh).toHaveAttribute("rel", "noopener noreferrer");
		expect(fnrh).toHaveAccessibleName(/abre em nova aba/i);

		expect(
			screen.getByText(
				/o observatório não se integra ao cadastur nem à fnrh digital/i,
			),
		).toBeInTheDocument();
	});

	it("groups the institutional logos by level", () => {
		render(<About />);

		const groups = [
			{
				label: "Marca do projeto",
				logos: [
					/observatório do turismo de santa rita do sapucaí/i,
					/santa rita do sapucaí – cidade criativa, cidade feliz/i,
				],
			},
			{
				label: "Realização e apoio",
				logos: [
					/prefeitura municipal de santa rita do sapucaí/i,
					/secretaria municipal de cultura, esporte, lazer e turismo/i,
					/conselho municipal de turismo/i,
				],
			},
			{
				label: "Contexto regional",
				logos: [/circuito turístico caminhos da mantiqueira/i, /minas gerais/i],
			},
		];

		for (const group of groups) {
			const container = screen.getByText(group.label).parentElement;

			expect(container).not.toBeNull();

			for (const name of group.logos) {
				expect(
					within(container as HTMLElement).getByRole("img", { name }),
				).toBeInTheDocument();
			}
		}
	});
});
