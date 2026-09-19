import { indicators } from "./indicators";

export const dashboardEvolution = indicators
	.filter(
		(indicator) =>
			indicator.name === "Meios de hospedagem" &&
			indicator.status === "published",
	)
	.sort((a, b) => a.period - b.period)
	.map((indicator) => ({
		year: indicator.period,
		establishments: indicator.value,
	}));

const sectorIndicatorNames = {
	Hospedagem: "Meios de hospedagem",
	Alimentação: "Estabelecimentos de alimentação",
	Serviços: "Empresas de serviços turísticos",
} as const;

export function getSectorDistribution(period: number) {
	return Object.entries(sectorIndicatorNames).map(([sector, indicatorName]) => {
		const indicator = indicators.find(
			(item) =>
				item.name === indicatorName &&
				item.period === period &&
				item.status === "published",
		);

		return {
			sector,
			value: indicator?.value ?? 0,
		};
	});
}
