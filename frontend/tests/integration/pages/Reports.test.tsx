import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Reports } from "../../../src/pages/Reports/Reports";

describe("Reports page", () => {
	it("renders the reports page", () => {
		render(<Reports />);

		expect(
			screen.getByRole("heading", {
				level: 1,
				name: /relatórios e pesquisas/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByText(
				/os relatórios apresentados nesta versão são demonstrativos/i,
			),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: /publicações disponíveis/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("searchbox", {
				name: /buscar relatório/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("combobox", {
				name: /ano/i,
			}),
		).toBeInTheDocument();
	});

	it("shows only published reports", () => {
		render(<Reports />);

		expect(
			screen.getByRole("heading", {
				name: "Relatório Anual do Turismo 2026",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2026",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Boletim do Turismo — 1º semestre de 2026",
			}),
		).toBeInTheDocument();

		expect(
			screen.queryByRole("heading", {
				name: "Boletim do Turismo — 2º semestre de 2026",
			}),
		).not.toBeInTheDocument();

		expect(screen.getByText(/6 publicações encontradas/i)).toBeInTheDocument();
	});

	it("filters reports by search term", () => {
		render(<Reports />);

		const searchInput = screen.getByRole("searchbox", {
			name: /buscar relatório/i,
		});

		fireEvent.change(searchInput, {
			target: {
				value: "Perfil",
			},
		});

		expect(
			screen.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2026",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2025",
			}),
		).toBeInTheDocument();

		expect(
			screen.queryByRole("heading", {
				name: "Relatório Anual do Turismo 2026",
			}),
		).not.toBeInTheDocument();

		expect(screen.getByText(/2 publicações encontradas/i)).toBeInTheDocument();
	});

	it("filters reports by year", () => {
		render(<Reports />);

		const yearSelect = screen.getByRole("combobox", {
			name: /ano/i,
		});

		fireEvent.change(yearSelect, {
			target: {
				value: "2025",
			},
		});

		expect(yearSelect).toHaveValue("2025");

		expect(
			screen.getByRole("heading", {
				name: "Relatório Anual do Turismo 2025",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2025",
			}),
		).toBeInTheDocument();

		expect(
			screen.queryByRole("heading", {
				name: "Relatório Anual do Turismo 2026",
			}),
		).not.toBeInTheDocument();

		expect(screen.getByText(/2 publicações encontradas/i)).toBeInTheDocument();
	});

	it("combines search and year filters", () => {
		render(<Reports />);

		const searchInput = screen.getByRole("searchbox", {
			name: /buscar relatório/i,
		});

		const yearSelect = screen.getByRole("combobox", {
			name: /ano/i,
		});

		fireEvent.change(searchInput, {
			target: {
				value: "Perfil",
			},
		});

		fireEvent.change(yearSelect, {
			target: {
				value: "2025",
			},
		});

		expect(
			screen.getByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2025",
			}),
		).toBeInTheDocument();

		expect(
			screen.queryByRole("heading", {
				name: "Pesquisa de Perfil do Turista 2026",
			}),
		).not.toBeInTheDocument();

		expect(screen.getByText(/1 publicação encontrada/i)).toBeInTheDocument();
	});

	it("shows an empty state when no report matches the filters", () => {
		render(<Reports />);

		const searchInput = screen.getByRole("searchbox", {
			name: /buscar relatório/i,
		});

		fireEvent.change(searchInput, {
			target: {
				value: "relatório que não existe",
			},
		});

		expect(
			screen.getByRole("heading", {
				name: /nenhuma publicação encontrada/i,
			}),
		).toBeInTheDocument();

		expect(screen.getByText(/0 publicações encontradas/i)).toBeInTheDocument();

		expect(
			screen.getByText(
				/tente alterar o termo de busca ou selecionar outro ano/i,
			),
		).toBeInTheDocument();
	});

	it("shows the available years in descending order", () => {
		render(<Reports />);

		const yearSelect = screen.getByRole("combobox", {
			name: /ano/i,
		});

		const options = within(yearSelect).getAllByRole("option");

		expect(options).toHaveLength(4);

		expect(options[0]).toHaveTextContent("Todos os anos");
		expect(options[1]).toHaveTextContent("2026");
		expect(options[2]).toHaveTextContent("2025");
		expect(options[3]).toHaveTextContent("2024");
	});
});
