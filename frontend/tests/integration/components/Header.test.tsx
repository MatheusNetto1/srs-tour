import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { Header } from "../../../src/components/layout/Header";

function renderHeader(initialEntry = "/") {
	return render(
		<MemoryRouter initialEntries={[initialEntry]}>
			<Header />
		</MemoryRouter>,
	);
}

describe("Header", () => {
	it("renderiza a logo e os links da navegação principal", () => {
		renderHeader();

		expect(
			screen.getByRole("link", {
				name: "Página inicial do Observatório do Turismo",
			}),
		).toBeInTheDocument();

		const navigation = screen.getByRole("navigation", {
			name: "Navegação principal",
		});

		expect(
			within(navigation)
				.getAllByRole("link")
				.map((link) => link.textContent),
		).toEqual(["Início", "Indicadores", "Relatórios", "Sobre"]);
	});

	it("destaca o link correspondente à rota atual", () => {
		renderHeader("/indicadores");

		const navigation = screen.getByRole("navigation", {
			name: "Navegação principal",
		});
		const activeLink = within(navigation).getByRole("link", {
			name: "Indicadores",
		});

		expect(activeLink).toHaveClass("text-brand-blue");
	});

	it("abre e fecha o menu mobile", () => {
		renderHeader();

		const openButton = screen.getByRole("button", {
			name: "Abrir menu",
		});

		expect(openButton).toHaveAttribute("aria-expanded", "false");
		expect(
			screen.queryByRole("navigation", { name: "Navegação mobile" }),
		).not.toBeInTheDocument();

		fireEvent.click(openButton);

		const closeButton = screen.getByRole("button", {
			name: "Fechar menu",
		});

		expect(closeButton).toHaveAttribute("aria-expanded", "true");
		expect(
			screen.getByRole("navigation", { name: "Navegação mobile" }),
		).toBeInTheDocument();

		fireEvent.click(closeButton);

		expect(
			screen.queryByRole("navigation", { name: "Navegação mobile" }),
		).not.toBeInTheDocument();
	});

	it("fecha o menu mobile ao clicar em um link", () => {
		renderHeader();

		fireEvent.click(screen.getByRole("button", { name: "Abrir menu" }));

		const mobileNavigation = screen.getByRole("navigation", {
			name: "Navegação mobile",
		});

		fireEvent.click(
			within(mobileNavigation).getByRole("link", { name: "Sobre" }),
		);

		expect(
			screen.queryByRole("navigation", { name: "Navegação mobile" }),
		).not.toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Abrir menu" })).toHaveAttribute(
			"aria-expanded",
			"false",
		);
	});
});
