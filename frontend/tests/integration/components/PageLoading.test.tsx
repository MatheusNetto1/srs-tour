import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PageLoading } from "../../../src/components/ui/PageLoading";

describe("PageLoading", () => {
	it("anuncia o carregamento da página como status", () => {
		render(<PageLoading />);

		expect(screen.getByRole("status")).toHaveTextContent(
			"Carregando página...",
		);
	});
});
