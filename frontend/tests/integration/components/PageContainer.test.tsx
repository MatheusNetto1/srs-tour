import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PageContainer } from "../../../src/components/layout/PageContainer";

describe("PageContainer", () => {
	it("renderiza os filhos e usa o tamanho padrão", () => {
		render(
			<PageContainer>
				<span data-testid="content">Conteúdo da página</span>
			</PageContainer>,
		);

		const content = screen.getByTestId("content");
		const container = content.parentElement;

		expect(content).toHaveTextContent("Conteúdo da página");
		expect(container).toHaveClass("max-w-7xl");
	});

	it("aplica o tamanho wide", () => {
		render(
			<PageContainer size="wide">
				<span data-testid="content">Conteúdo amplo</span>
			</PageContainer>,
		);

		expect(screen.getByTestId("content").parentElement).toHaveClass(
			"max-w-[1440px]",
		);
	});

	it("repassa a classe personalizada", () => {
		render(
			<PageContainer className="custom-class">
				<span data-testid="content">Conteúdo</span>
			</PageContainer>,
		);

		expect(screen.getByTestId("content").parentElement).toHaveClass(
			"custom-class",
		);
	});
});
