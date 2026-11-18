import { act, fireEvent, render, screen, within } from "@testing-library/react";
import type { ComponentType } from "react";
import { createMemoryRouter, Link, RouterProvider } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { PublicLayout } from "../../../src/layouts/PublicLayout";

// O PublicLayout usa useNavigation, que só funciona dentro de um data router.
describe("PublicLayout", () => {
	it("renderiza header, conteúdo da rota filha e footer", () => {
		const router = createMemoryRouter(
			[
				{
					element: <PublicLayout />,
					children: [
						{ path: "/teste", element: <h1>Conteúdo da rota filha</h1> },
					],
				},
			],
			{ initialEntries: ["/teste"] },
		);

		render(<RouterProvider router={router} />);

		expect(screen.getByRole("banner")).toBeInTheDocument();

		const main = screen.getByRole("main");

		expect(
			within(main).getByRole("heading", {
				name: "Conteúdo da rota filha",
			}),
		).toBeInTheDocument();

		expect(screen.getByRole("contentinfo")).toBeInTheDocument();
	});

	it("anuncia o carregamento enquanto a próxima página chega", async () => {
		let resolvePage: (page: { Component: ComponentType }) => void = () => {};
		const pageLoaded = new Promise<{ Component: ComponentType }>((resolve) => {
			resolvePage = resolve;
		});

		const router = createMemoryRouter(
			[
				{
					element: <PublicLayout />,
					children: [
						{
							path: "/",
							element: <Link to="/lenta">Abrir página lenta</Link>,
						},
						{ path: "/lenta", lazy: () => pageLoaded },
					],
				},
			],
			{ initialEntries: ["/"] },
		);

		render(<RouterProvider router={router} />);

		const status = screen.getByRole("status");

		expect(status).toBeEmptyDOMElement();

		fireEvent.click(screen.getByRole("link", { name: "Abrir página lenta" }));

		expect(status).toHaveTextContent("Carregando página...");

		await act(async () => {
			resolvePage({ Component: () => <h1>Página lenta</h1> });
		});

		expect(
			await screen.findByRole("heading", { name: "Página lenta" }),
		).toBeInTheDocument();
		expect(status).toBeEmptyDOMElement();
	});
});
