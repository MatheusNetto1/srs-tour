export type IndicatorStatus = "draft" | "published";

export interface Indicator {
	id: string;
	name: string;
	sector: string;
	period: number;
	value: number;
	unit: string;
	status: IndicatorStatus;
	updatedAt: string;
}
