import { Outlet, useNavigation } from "react-router-dom";
import { Footer } from "../components/layout/Footer";
import { Header } from "../components/layout/Header";

export function PublicLayout() {
	const navigation = useNavigation();
	const isNavigating = navigation.state === "loading";

	return (
		<div className="flex min-h-screen flex-col bg-slate-50 text-slate-950">
			{/* Barra fixa no topo enquanto a próxima página carrega: não ocupa
			espaço no fluxo, então não desloca o layout. */}
			{isNavigating && (
				<div
					aria-hidden="true"
					className="pointer-events-none fixed inset-x-0 top-0 z-50 h-1 animate-pulse bg-brand-gradient"
				/>
			)}

			{/* Região sempre presente para que o leitor de tela anuncie a mudança. */}
			<p role="status" className="sr-only">
				{isNavigating ? "Carregando página..." : ""}
			</p>

			<Header />

			<main className="flex-1">
				<Outlet />
			</main>

			<Footer />
		</div>
	);
}
