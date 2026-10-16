import { createBrowserRouter } from "react-router-dom";

import { PublicLayout } from "../layouts/PublicLayout";
import { About } from "../pages/About/About";
import { Home } from "../pages/Home/Home";
import { Indicators } from "../pages/Indicators/Indicators";
import { Reports } from '../pages/Reports/Reports";

export const router = createBrowserRouter([
	{
		element: <PublicLayout />,
		children: [
			{ path: "/", element: <Home /> },
			{ path: "/indicadores", element: <Indicators /> },
			{ path: "/relatorios", element: <Reports /> },
			{ path: "/sobre", element: <About /> },
		],
	},
]);
