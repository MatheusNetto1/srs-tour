export type ReportCategory =
	| "Pesquisa"
	| "Relatório anual"
	| "Boletim"
	| "Estudo";

export type ReportStatus = "published" | "draft";

export interface Report {
	id: string;
	title: string;
	description: string;
	category: ReportCategory;
	year: number;
	publishedAt: string;
	status: ReportStatus;
	file?: string;
}
