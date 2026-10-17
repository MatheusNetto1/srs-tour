import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Button } from "../../../src/components/ui/Button";

describe("Button", () => {
	it('usa type="button" por padrão', () => {
		render(<Button>Salvar</Button>);

		expect(screen.getByRole("button", { name: "Salvar" })).toHaveAttribute(
			"type",
			"button",
		);
	});

	it("aplica as classes das variantes primary e danger", () => {
		const { rerender } = render(<Button variant="primary">Confirmar</Button>);

		expect(screen.getByRole("button", { name: "Confirmar" })).toHaveClass(
			"bg-brand-blue",
		);

		rerender(<Button variant="danger">Excluir</Button>);

		expect(screen.getByRole("button", { name: "Excluir" })).toHaveClass(
			"bg-red-600",
		);
	});

	it("não executa o clique quando está desabilitado", () => {
		const handleClick = vi.fn();

		render(
			<Button disabled onClick={handleClick}>
				Salvar
			</Button>,
		);

		const button = screen.getByRole("button", { name: "Salvar" });

		expect(button).toBeDisabled();

		fireEvent.click(button);

		expect(handleClick).not.toHaveBeenCalled();
	});
});
