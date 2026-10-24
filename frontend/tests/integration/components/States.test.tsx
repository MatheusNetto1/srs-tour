import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiError } from "../../../src/api/errors";
import { EmptyState } from "../../../src/components/ui/EmptyState";
import { ErrorState } from "../../../src/components/ui/ErrorState";
import { LoadingState } from "../../../src/components/ui/LoadingState";
import { renderApp } from "../../utils/render";

describe("LoadingState", () => {
	it("anuncia o carregamento como status", () => {
		renderApp(<LoadingState />);

		expect(screen.getByRole("status")).toHaveTextContent("Carregando...");
	});
});

describe("EmptyState", () => {
	it("mostra a mensagem padrão e a customizada", () => {
		const { rerender } = renderApp(<EmptyState />);

		expect(screen.getByRole("status")).toHaveTextContent(
			"Nenhum resultado encontrado.",
		);

		rerender(<EmptyState message="Sem relatórios." />);

		expect(screen.getByRole("status")).toHaveTextContent("Sem relatórios.");
	});
});

describe("ErrorState", () => {
	const error = new ApiError({
		status: 500,
		code: "internal_error",
		detail: "Erro inesperado no servidor.",
	});

	it("mostra error.detail como alerta", () => {
		renderApp(<ErrorState error={error} onRetry={() => {}} />);

		expect(screen.getByRole("alert")).toHaveTextContent(
			"Erro inesperado no servidor.",
		);
	});

	it("chama onRetry ao clicar em Tentar novamente", () => {
		const onRetry = vi.fn();

		renderApp(<ErrorState error={error} onRetry={onRetry} />);

		fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));

		expect(onRetry).toHaveBeenCalledTimes(1);
	});
});
