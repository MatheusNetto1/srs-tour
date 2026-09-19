import {
	BarChart3,
	BedDouble,
	BriefcaseBusiness,
	Building2,
	Hotel,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
	Bar,
	BarChart,
	CartesianGrid,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

import { PageContainer } from "../../components/layout/PageContainer";
import { Card } from "../../components/ui/Card";
import { DemoNotice } from "../../components/ui/DemoNotice";
import { Select } from "../../components/ui/Select";
import {
	dashboardEvolution,
	getSectorDistribution,
} from "../../mocks/dashboard";
import { indicators } from "../../mocks/indicators";
import type { IndicatorSector } from "../../types/indicator";

type SectorFilter = "all" | IndicatorSector;

const summaryIndicators = [
	{
		name: "Meios de hospedagem",
		icon: Hotel,
	},
	{
		name: "Leitos disponíveis",
		icon: BedDouble,
	},
	{
		name: "Empregos no turismo",
		icon: BriefcaseBusiness,
	},
];

export function Indicators() {
	const [selectedSector, setSelectedSector] = useState<SectorFilter>("all");
	const [selectedPeriod, setSelectedPeriod] = useState(2026);

	const publishedIndicators = useMemo(
		() => indicators.filter((indicator) => indicator.status === "published"),
		[],
	);

	const filteredIndicators = useMemo(
		() =>
			publishedIndicators.filter((indicator) => {
				const matchesSector =
					selectedSector === "all" || indicator.sector === selectedSector;

				const matchesPeriod = indicator.period === selectedPeriod;

				return matchesSector && matchesPeriod;
			}),
		[publishedIndicators, selectedPeriod, selectedSector],
	);

	const summary = useMemo(
		() =>
			summaryIndicators
				.map((summaryIndicator) => {
					const indicator = publishedIndicators.find(
						(item) =>
							item.name === summaryIndicator.name &&
							item.period === selectedPeriod,
					);

					if (!indicator) {
						return null;
					}

					return {
						...indicator,
						icon: summaryIndicator.icon,
					};
				})
				.filter((indicator) => indicator !== null),
		[publishedIndicators, selectedPeriod],
	);

	const sectorDistribution = useMemo(
		() => getSectorDistribution(selectedPeriod),
		[selectedPeriod],
	);

	return (
		<div className="bg-slate-50">
			<section className="border-b border-slate-200 bg-white">
				<PageContainer size="wide" className="py-14">
					<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-blue">
						Dados
					</p>

					<h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950">
						Indicadores turísticos
					</h1>

					<p className="mt-4 max-w-2xl leading-7 text-slate-600">
						Explore informações sobre a atividade turística de Santa Rita do
						Sapucaí por meio de indicadores e visualizações.
					</p>
				</PageContainer>
			</section>

			<PageContainer size="wide" className="py-10">
				<DemoNotice />

				<section className="mt-8">
					<div className="grid gap-4 sm:grid-cols-2 lg:max-w-xl">
						<Select
							id="sector"
							label="Setor"
							value={selectedSector}
							onChange={(event) =>
								setSelectedSector(event.target.value as SectorFilter)
							}
						>
							<option value="all">Todos os setores</option>
							<option value="Hospedagem">Hospedagem</option>
							<option value="Alimentação">Alimentação</option>
							<option value="Serviços">Serviços</option>
							<option value="Geral">Geral</option>
						</Select>

						<Select
							id="period"
							label="Período"
							value={selectedPeriod}
							onChange={(event) =>
								setSelectedPeriod(Number(event.target.value))
							}
						>
							<option value={2026}>2026</option>
							<option value={2025}>2025</option>
							<option value={2024}>2024</option>
						</Select>
					</div>
				</section>

				<section className="mt-10">
					<div className="grid gap-5 md:grid-cols-3">
						{summary.map((item) => {
							const Icon = item.icon;

							return (
								<Card key={item.name} className="p-6">
									<div className="flex items-start justify-between gap-4">
										<div>
											<p className="text-sm font-medium text-slate-500">
												{item.name}
											</p>

											<p className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
												{item.value.toLocaleString("pt-BR")}
											</p>

											<p className="mt-1 text-xs text-slate-500">{item.unit}</p>
										</div>

										<div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-brand-blue">
											<Icon size={21} />
										</div>
									</div>
								</Card>
							);
						})}
					</div>
				</section>

				<section className="mt-10 grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
					<Card className="p-6">
						<div className="flex items-center gap-3">
							<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-brand-blue">
								<BarChart3 size={20} />
							</div>

							<div>
								<h2 className="font-semibold text-slate-950">
									Evolução dos estabelecimentos
								</h2>

								<p className="text-sm text-slate-500">
									Meios de hospedagem por ano
								</p>
							</div>
						</div>

						<div className="mt-8 h-80">
							<ResponsiveContainer width="100%" height="100%">
								<LineChart
									data={dashboardEvolution}
									margin={{
										top: 8,
										right: 12,
										left: 0,
										bottom: 0,
									}}
								>
									<CartesianGrid strokeDasharray="3 3" vertical={false} />

									<XAxis dataKey="year" />

									<YAxis allowDecimals={false} />

									<Tooltip />

									<Line
										type="monotone"
										dataKey="establishments"
										stroke="#0a4aad"
										strokeWidth={3}
										activeDot={{ r: 6 }}
									/>
								</LineChart>
							</ResponsiveContainer>
						</div>
					</Card>

					<Card className="p-6">
						<div className="flex items-center gap-3">
							<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50 text-brand-purple">
								<Building2 size={20} />
							</div>

							<div>
								<h2 className="font-semibold text-slate-950">
									Distribuição por setor
								</h2>

								<p className="text-sm text-slate-500">
									Estabelecimentos em {selectedPeriod}
								</p>
							</div>
						</div>

						<div className="mt-8 h-80">
							<ResponsiveContainer width="100%" height="100%">
								<BarChart
									data={sectorDistribution}
									margin={{
										top: 8,
										right: 12,
										left: 0,
										bottom: 0,
									}}
								>
									<CartesianGrid strokeDasharray="3 3" vertical={false} />

									<XAxis dataKey="sector" />

									<YAxis allowDecimals={false} />

									<Tooltip />

									<Bar dataKey="value" fill="#6c5ce0" radius={[6, 6, 0, 0]} />
								</BarChart>
							</ResponsiveContainer>
						</div>
					</Card>
				</section>

				<section className="mt-14">
					<div>
						<h2 className="text-2xl font-bold tracking-tight text-slate-950">
							Indicadores disponíveis
						</h2>

						<p className="mt-2 text-sm text-slate-600">
							Consulte os indicadores publicados no Observatório.
						</p>
					</div>

					<Card className="mt-6 overflow-hidden">
						<div className="overflow-x-auto">
							<table className="w-full text-left text-sm">
								<thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
									<tr>
										<th className="px-6 py-4 font-semibold">Indicador</th>

										<th className="px-6 py-4 font-semibold">Setor</th>

										<th className="px-6 py-4 font-semibold">Período</th>

										<th className="px-6 py-4 text-right font-semibold">
											Valor
										</th>
									</tr>
								</thead>

								<tbody className="divide-y divide-slate-100">
									{filteredIndicators.map((indicator) => (
										<tr
											key={indicator.id}
											className="bg-white transition-colors hover:bg-slate-50"
										>
											<td className="px-6 py-4 font-medium text-slate-900">
												{indicator.name}
											</td>

											<td className="px-6 py-4 text-slate-600">
												{indicator.sector}
											</td>

											<td className="px-6 py-4 text-slate-600">
												{indicator.period}
											</td>

											<td className="px-6 py-4 text-right font-semibold text-slate-900">
												{indicator.value.toLocaleString("pt-BR")}{" "}
												<span className="font-normal text-slate-500">
													{indicator.unit}
												</span>
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>

						{filteredIndicators.length === 0 && (
							<div className="px-6 py-12 text-center">
								<p className="font-medium text-slate-700">
									Nenhum indicador encontrado
								</p>

								<p className="mt-1 text-sm text-slate-500">
									Tente selecionar outro setor ou período.
								</p>
							</div>
						)}
					</Card>
				</section>
			</PageContainer>
		</div>
	);
}
