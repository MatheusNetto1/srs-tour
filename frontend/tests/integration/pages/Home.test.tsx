import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "../../../src/App";

describe("Home page", () => {
	it("renders the main institutional content", () => {
		render(<App />);

		expect(
			screen.getByRole("heading", {
				level: 1,
				name: /dados para compreender e fortalecer o turismo/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("link", {
				name: /explorar indicadores/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("link", {
				name: /ver relatórios/i,
			}),
		).toBeInTheDocument();
	});

	it("renders the tourism indicators section", () => {
		render(<App />);

		expect(
			screen.getByRole("heading", {
				name: /turismo em números/i,
			}),
		).toBeInTheDocument();

		expect(screen.getByText("Meios de hospedagem")).toBeInTheDocument();
		expect(screen.getByText("Leitos disponíveis")).toBeInTheDocument();
		expect(screen.getByText("Empresas do setor")).toBeInTheDocument();
		expect(screen.getByText("Empregos no turismo")).toBeInTheDocument();
	});

	it("renders the observatory resources", () => {
		render(<App />);

		expect(
			screen.getByRole("heading", {
				name: /explore o observatório/i,
			}),
		).toBeInTheDocument();

		expect(screen.getByText("Indicadores turísticos")).toBeInTheDocument();
		expect(screen.getByText("Dashboard")).toBeInTheDocument();
		expect(screen.getByText("Relatórios públicos")).toBeInTheDocument();
	});
});
