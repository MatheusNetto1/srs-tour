import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { PageContainer } from "./PageContainer";

const navigation = [
	{ name: "Início", href: "/" },
	{ name: "Indicadores", href: "/indicadores" },
	{ name: "Relatórios", href: "/relatorios" },
	{ name: "Sobre", href: "/sobre" },
];

export function Header() {
	const [menuOpen, setMenuOpen] = useState(false);

	return (
		<header className="border-b border-slate-200 bg-white">
			<PageContainer>
				<div className="flex h-20 items-center justify-between">
					<Link
						to="/"
						className="flex items-center gap-3"
						aria-label="Página inicial do Observatório do Turismo"
					>
						<span className="font-bold text-slate-900">
							Observatório do Turismo
						</span>
					</Link>

					<nav
						className="hidden items-center gap-8 md:flex"
						aria-label="Navegação principal"
					>
						{navigation.map((item) => (
							<NavLink
								key={item.href}
								to={item.href}
								className={({ isActive }) =>
									[
										"text-sm font-medium transition-colors",
										isActive
											? "text-[#0A4AAD]"
											: "text-slate-600 hover:text-slate-950",
									].join(" ")
								}
							>
								{item.name}
							</NavLink>
						))}
					</nav>

					<button
						type="button"
						className="rounded-lg p-2 text-slate-700 md:hidden"
						onClick={() => setMenuOpen((current) => !current)}
						aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
						aria-expanded={menuOpen}
					>
						{menuOpen ? <X /> : <Menu />}
					</button>
				</div>

				{menuOpen && (
					<nav
						className="border-t border-slate-100 py-4 md:hidden"
						aria-label="Navegação mobile"
					>
						<div className="flex flex-col gap-2">
							{navigation.map((item) => (
								<NavLink
									key={item.href}
									to={item.href}
									onClick={() => setMenuOpen(false)}
									className={({ isActive }) =>
										[
											"rounded-lg px-3 py-2 text-sm font-medium",
											isActive
												? "bg-blue-50 text-[#0A4AAD]"
												: "text-slate-600 hover:bg-slate-50",
										].join(" ")
									}
								>
									{item.name}
								</NavLink>
							))}
						</div>
					</nav>
				)}
			</PageContainer>
		</header>
	);
}
