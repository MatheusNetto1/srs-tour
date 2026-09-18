import { BarChart3, FileText, LayoutDashboard, LogOut } from "lucide-react";
import { NavLink } from "react-router-dom";

const navigation = [
	{
		name: "Visão geral",
		href: "/admin",
		icon: LayoutDashboard,
		end: true,
	},
	{
		name: "Indicadores",
		href: "/admin/indicadores",
		icon: BarChart3,
	},
	{
		name: "Relatórios",
		href: "/admin/relatorios",
		icon: FileText,
	},
];

export function AdminSidebar() {
	return (
		<aside className="flex w-64 flex-col border-r border-slate-200 bg-white">
			<div className="border-b border-slate-200 p-6">
				<p className="font-bold text-slate-950">Observatório</p>

				<p className="mt-1 text-xs text-slate-500">Administração</p>
			</div>

			<nav
				className="flex flex-1 flex-col gap-1 p-4"
				aria-label="Navegação administrativa"
			>
				{navigation.map((item) => {
					const Icon = item.icon;

					return (
						<NavLink
							key={item.href}
							to={item.href}
							end={item.end}
							className={({ isActive }) =>
								[
									"flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
									isActive
										? "bg-blue-50 text-[#0A4AAD]"
										: "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
								].join(" ")
							}
						>
							<Icon size={18} />

							{item.name}
						</NavLink>
					);
				})}
			</nav>

			<div className="border-t border-slate-200 p-4">
				<NavLink
					to="/"
					className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100"
				>
					<LogOut size={18} />
					Sair
				</NavLink>
			</div>
		</aside>
	);
}
