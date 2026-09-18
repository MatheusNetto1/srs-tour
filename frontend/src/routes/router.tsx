import { createHashRouter } from "react-router-dom";

import { AdminLayout } from "../layouts/AdminLayout";
import { PublicLayout } from "../layouts/PublicLayout";

import { About } from "../pages/About/About";
import { AdminDashboard } from "../pages/Admin/Dashboard/Dashboard";
import { AdminIndicators } from "../pages/Admin/Indicators/Indicators";
import { Login } from "../pages/Admin/Login/Login";
import { AdminReports } from "../pages/Admin/Reports/Reports";
import { Home } from "../pages/Home/Home";
import { Indicators } from "../pages/Indicators/Indicators";
import { Reports } from "../pages/Reports/Reports";

export const router = createHashRouter([
	{
		element: <PublicLayout />,
		children: [
			{
				path: "/",
				element: <Home />,
			},
			{
				path: "/indicadores",
				element: <Indicators />,
			},
			{
				path: "/relatorios",
				element: <Reports />,
			},
			{
				path: "/sobre",
				element: <About />,
			},
		],
	},
	{
		path: "/admin/login",
		element: <Login />,
	},
	{
		path: "/admin",
		element: <AdminLayout />,
		children: [
			{
				index: true,
				element: <AdminDashboard />,
			},
			{
				path: "indicadores",
				element: <AdminIndicators />,
			},
			{
				path: "relatorios",
				element: <AdminReports />,
			},
		],
	},
]);
