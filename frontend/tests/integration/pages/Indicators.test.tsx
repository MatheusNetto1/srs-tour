import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Indicators } from "../../../src/pages/Indicators/Indicators";

describe("Indicators page", () => {
	it("renders the indicators dashboard", () => {
		render(<Indicators />);

		expect(
			screen.getByRole("heading", {
				level: 1,
				name: /indicadores turísticos/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByText(
				/os dados apresentados nesta versão são demonstrativos/i,
			),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: /evolução dos estabelecimentos/i,
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("heading", {
				name: /distribuição por setor/i,
			}),
		).toBeInTheDocument();
	});

	it("shows only published indicators for the default period", () => {
		render(<Indicators />);

		const table = screen.getByRole("table");

		expect(within(table).getByText("Meios de hospedagem")).toBeInTheDocument();

		expect(within(table).getByText("Leitos disponíveis")).toBeInTheDocument();

		expect(
			within(table).getByText("Estabelecimentos de alimentação"),
		).toBeInTheDocument();

		expect(
			within(table).getByText("Empresas de serviços turísticos"),
		).toBeInTheDocument();

		expect(within(table).getByText("Empregos no turismo")).toBeInTheDocument();

		expect(
			within(table).queryByText("Fluxo estimado de visitantes"),
		).not.toBeInTheDocument();
	});

	it("filters indicators by sector", () => {
		render(<Indicators />);

		const sectorSelect = screen.getByRole("combobox", {
			name: /setor/i,
		});

		fireEvent.change(sectorSelect, {
			target: {
				value: "Alimentação",
			},
		});

		const table = screen.getByRole("table");

		expect(
			within(table).getByText("Estabelecimentos de alimentação"),
		).toBeInTheDocument();

		expect(
			within(table).queryByText("Meios de hospedagem"),
		).not.toBeInTheDocument();

		expect(
			within(table).queryByText("Empresas de serviços turísticos"),
		).not.toBeInTheDocument();

		expect(
			within(table).queryByText("Empregos no turismo"),
		).not.toBeInTheDocument();
	});

	it("updates the dashboard when the period changes", () => {
		render(<Indicators />);

		const periodSelect = screen.getByRole("combobox", {
			name: /período/i,
		});

		fireEvent.change(periodSelect, {
			target: {
				value: "2025",
			},
		});

		expect(periodSelect).toHaveValue("2025");

		expect(screen.getByText(/estabelecimentos em 2025/i)).toBeInTheDocument();

		const table = screen.getByRole("table");

		expect(within(table).getAllByText("2025")).toHaveLength(5);

		expect(within(table).queryByText("2026")).not.toBeInTheDocument();
	});
});
