import { Menu, X } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router-dom";

import { logos } from "../../constants/assets";
import { PageContainer } from "./PageContainer";

const navigation = [
	{
		label: "Início",
		to: "/",
	},
	{
		label: "Indicadores",
		to: "/indicadores",
	},
	{
		label: "Relatórios",
		to: "/relatorios",
	},
	{
		label: "Sobre",
		to: "/sobre",
	},
];

export function Header() {
	const [isMenuOpen, setIsMenuOpen] = useState(false);

	return (
		<header className="border-b border-slate-200 bg-white">
			<PageContainer size="wide">
				<div className="flex h-24 items-center justify-between">
					<NavLink
						to="/"
						aria-label="Página inicial do Observatório do Turismo"
						className="flex items-center gap-3"
						onClick={() => setIsMenuOpen(false)}
					>
						<img
							src={logos.observatorio.black}
							alt="Observatório do Turismo de Santa Rita do Sapucaí"
							className="h-12 w-auto object-contain"
						/>
					</NavLink>

					<nav
						aria-label="Navegação principal"
						className="hidden items-center gap-8 md:flex"
					>
						{navigation.map((item) => (
							<NavLink
								key={item.to}
								to={item.to}
								className={({ isActive }) =>
									[
										"text-sm font-medium transition-colors",
										isActive
											? "text-brand-blue"
											: "text-slate-600 hover:text-slate-950",
									].join(" ")
								}
							>
								{item.label}
							</NavLink>
						))}
					</nav>

					<button
						type="button"
						aria-label={isMenuOpen ? "Fechar menu" : "Abrir menu"}
						aria-expanded={isMenuOpen}
						className="rounded-lg p-2 text-slate-700 md:hidden"
						onClick={() => setIsMenuOpen((current) => !current)}
					>
						{isMenuOpen ? <X size={24} /> : <Menu size={24} />}
					</button>
				</div>

				{isMenuOpen && (
					<nav
						aria-label="Navegação mobile"
						className="border-t border-slate-100 py-4 md:hidden"
					>
						<div className="flex flex-col gap-1">
							{navigation.map((item) => (
								<NavLink
									key={item.to}
									to={item.to}
									onClick={() => setIsMenuOpen(false)}
									className={({ isActive }) =>
										[
											"rounded-lg px-3 py-3 text-sm font-medium transition-colors",
											isActive
												? "bg-blue-50 text-brand-blue"
												: "text-slate-600 hover:bg-slate-50 hover:text-slate-950",
										].join(" ")
									}
								>
									{item.label}
								</NavLink>
							))}
						</div>
					</nav>
				)}
			</PageContainer>
		</header>
	);
}
