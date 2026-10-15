import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Card } from "../../../src/components/ui/Card";

describe("Card", () => {
	it("renderiza o conteúdo recebido", () => {
		render(
			<Card>
				<p>Conteúdo do card</p>
			</Card>,
		);

		expect(screen.getByText("Conteúdo do card")).toBeInTheDocument();
	});

	it("repassa className e atributos HTML", () => {
		render(
			<Card
				className="custom-card"
				data-testid="card"
				aria-label="Card de exemplo"
			>
				Conteúdo
			</Card>,
		);

		const card = screen.getByTestId("card");

		expect(card).toHaveClass("custom-card");
		expect(card).toHaveAttribute("aria-label", "Card de exemplo");
	});
});
