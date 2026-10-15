import { render, screen } from "@testing-library/react";
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
});
