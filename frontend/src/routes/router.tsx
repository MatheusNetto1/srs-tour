import { createBrowserRouter } from "react-router-dom";

import { PageLoading } from "../components/ui/PageLoading";
import { PublicLayout } from "../layouts/PublicLayout";

// As páginas são carregadas sob demanda: cada uma vira um chunk próprio, e o
// recharts (usado só em Indicadores) sai do bundle inicial. O PublicLayout
// continua estático. O fallback fica em cada rota filha para que, no primeiro
// carregamento, header e footer apareçam e só o conteúdo mostre o PageLoading.
export const router = createBrowserRouter([
	{
		element: <PublicLayout />,
		children: [
			{
				path: "/",
				hydrateFallbackElement: <PageLoading />,
				lazy: async () => ({
					Component: (await import("../pages/Home/Home")).Home,
				}),
			},
			{
				path: "/indicadores",
				hydrateFallbackElement: <PageLoading />,
				lazy: async () => ({
					Component: (await import("../pages/Indicators/Indicators"))
						.Indicators,
				}),
			},
			{
				path: "/relatorios",
				hydrateFallbackElement: <PageLoading />,
				lazy: async () => ({
					Component: (await import("../pages/Reports/Reports")).Reports,
				}),
			},
			{
				path: "/sobre",
				hydrateFallbackElement: <PageLoading />,
				lazy: async () => ({
					Component: (await import("../pages/About/About")).About,
				}),
			},
		],
	},
]);
