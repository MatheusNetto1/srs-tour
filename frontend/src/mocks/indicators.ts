import type { Indicator } from "../types/indicator";

export const indicators: Indicator[] = [
	{
		id: "1",
		name: "Meios de hospedagem",
		sector: "Hospedagem",
		period: 2026,
		value: 32,
		unit: "estabelecimentos",
		status: "published",
		updatedAt: "2026-09-10",
	},
	{
		id: "2",
		name: "Leitos disponíveis",
		sector: "Hospedagem",
		period: 2026,
		value: 742,
		unit: "leitos",
		status: "published",
		updatedAt: "2026-09-10",
	},
	{
		id: "3",
		name: "Empregos no setor",
		sector: "Geral",
		period: 2026,
		value: 1284,
		unit: "empregos",
		status: "published",
		updatedAt: "2026-09-02",
	},
	{
		id: "4",
		name: "Taxa de ocupação",
		sector: "Hospedagem",
		period: 2026,
		value: 68.4,
		unit: "%",
		status: "draft",
		updatedAt: "2026-09-15",
	},
];
