import { render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { PublicLayout } from "../../../src/layouts/PublicLayout";

describe("PublicLayout", () => {
	it("renderiza header, conteúdo da rota filha e footer", () => {
		render(
			<MemoryRouter initialEntries={["/teste"]}>
				<Routes>
					<Route element={<PublicLayout />}>
						<Route path="/teste" element={<h1>Conteúdo da rota filha</h1>} />
					</Route>
				</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByRole("banner")).toBeInTheDocument();

		const main = screen.getByRole("main");

		expect(
			within(main).getByRole("heading", {
				name: "Conteúdo da rota filha",
			}),
		).toBeInTheDocument();

		expect(screen.getByRole("contentinfo")).toBeInTheDocument();
	});
});
