import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Footer } from "../../../src/components/layout/Footer";

describe("Footer", () => {
	it("renderiza os logos institucionais com textos alternativos", () => {
		render(<Footer />);

		expect(
			screen.getByRole("img", {
				name: "Observatório do Turismo de Santa Rita do Sapucaí",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("img", {
				name: "Secretaria Municipal de Cultura, Esporte, Lazer e Turismo",
			}),
		).toBeInTheDocument();

		expect(
			screen.getByRole("img", {
				name: "Conselho Municipal de Turismo",
			}),
		).toBeInTheDocument();
	});

	it("renderiza os textos informativos do rodapé", () => {
		render(<Footer />);

		expect(
			screen.getByText(
				"Informação e dados para apoiar o desenvolvimento do turismo em Santa Rita do Sapucaí.",
			),
		).toBeInTheDocument();

		expect(
			screen.getByText("Observatório do Turismo de Santa Rita do Sapucaí"),
		).toBeInTheDocument();
	});
});
