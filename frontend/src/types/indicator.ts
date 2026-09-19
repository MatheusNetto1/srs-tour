export type IndicatorSector =
	| "Hospedagem"
	| "Alimentação"
	| "Serviços"
	| "Geral";

export type IndicatorStatus = "published" | "draft";

export interface Indicator {
	id: string;
	name: string;
	sector: IndicatorSector;
	period: number;
	value: number;
	unit: string;
	status: IndicatorStatus;
}
