import { Outlet } from "react-router-dom";
import { AdminSidebar } from "../components/layout/AdminSidebar";

export function AdminLayout() {
	return (
		<div className="flex min-h-screen bg-slate-50 text-slate-950">
			<AdminSidebar />

			<main className="min-w-0 flex-1">
				<div className="mx-auto max-w-7xl p-8">
					<Outlet />
				</div>
			</main>
		</div>
	);
}
