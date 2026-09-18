export type ReportStatus = "draft" | "published";

export interface Report {
	id: string;
	title: string;
	description: string;
	year: number;
	fileUrl: string;
	status: ReportStatus;
	publishedAt?: string;
}
