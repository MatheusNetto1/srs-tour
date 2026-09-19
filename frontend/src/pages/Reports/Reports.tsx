import {
	CalendarDays,
	Download,
	FileSearch,
	FileText,
	Search,
} from "lucide-react";
import { useMemo, useState } from "react";

import { PageContainer } from "../../components/layout/PageContainer";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { DemoNotice } from "../../components/ui/DemoNotice";
import { Select } from "../../components/ui/Select";
import { reports } from "../../mocks/reports";

type YearFilter = "all" | number;

function formatDate(date: string) {
	return new Intl.DateTimeFormat("pt-BR", {
		day: "2-digit",
		month: "long",
		year: "numeric",
		timeZone: "UTC",
	}).format(new Date(date));
}

export function Reports() {
	const [search, setSearch] = useState("");
	const [selectedYear, setSelectedYear] = useState<YearFilter>("all");

	const publishedReports = useMemo(
		() =>
			reports
				.filter((report) => report.status === "published")
				.sort(
					(a, b) =>
						new Date(b.publishedAt).getTime() -
						new Date(a.publishedAt).getTime(),
				),
		[],
	);

	const availableYears = useMemo(
		() =>
			[...new Set(publishedReports.map((report) => report.year))].sort(
				(a, b) => b - a,
			),
		[publishedReports],
	);

	const filteredReports = useMemo(() => {
		const normalizedSearch = search.trim().toLocaleLowerCase("pt-BR");

		return publishedReports.filter((report) => {
			const matchesYear =
				selectedYear === "all" || report.year === selectedYear;

			const matchesSearch =
				normalizedSearch.length === 0 ||
				report.title.toLocaleLowerCase("pt-BR").includes(normalizedSearch) ||
				report.description
					.toLocaleLowerCase("pt-BR")
					.includes(normalizedSearch) ||
				report.category.toLocaleLowerCase("pt-BR").includes(normalizedSearch);

			return matchesYear && matchesSearch;
		});
	}, [publishedReports, search, selectedYear]);

	return (
		<div className="bg-slate-50">
			<section className="border-b border-slate-200 bg-white">
				<PageContainer size="wide" className="py-14">
					<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-blue">
						Publicações
					</p>

					<h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950">
						Relatórios e pesquisas
					</h1>

					<p className="mt-4 max-w-2xl leading-7 text-slate-600">
						Consulte pesquisas, estudos, boletins e relatórios produzidos pelo
						Observatório do Turismo de Santa Rita do Sapucaí.
					</p>
				</PageContainer>
			</section>

			<PageContainer size="wide" className="py-10">
				<DemoNotice>
					Os relatórios apresentados nesta versão são demonstrativos. Os
					documentos oficiais serão disponibilizados para consulta e download
					conforme forem publicados pelo Observatório.
				</DemoNotice>

				<section className="mt-8">
					<div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_240px]">
						<div className="flex flex-col gap-2">
							<label
								htmlFor="report-search"
								className="text-sm font-medium text-slate-700"
							>
								Buscar relatório
							</label>

							<div className="relative">
								<Search
									size={18}
									className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
								/>

								<input
									id="report-search"
									type="search"
									value={search}
									onChange={(event) => setSearch(event.target.value)}
									placeholder="Buscar por título, descrição ou categoria..."
									className="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-700 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20"
								/>
							</div>
						</div>

						<Select
							id="report-year"
							label="Ano"
							value={selectedYear}
							onChange={(event) =>
								setSelectedYear(
									event.target.value === "all"
										? "all"
										: Number(event.target.value),
								)
							}
						>
							<option value="all">Todos os anos</option>

							{availableYears.map((year) => (
								<option key={year} value={year}>
									{year}
								</option>
							))}
						</Select>
					</div>
				</section>

				<section className="mt-10">
					<div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
						<div>
							<h2 className="text-2xl font-bold tracking-tight text-slate-950">
								Publicações disponíveis
							</h2>

							<p className="mt-2 text-sm text-slate-600">
								Documentos publicados para consulta pública.
							</p>
						</div>

						<p className="text-sm text-slate-500">
							{filteredReports.length}{" "}
							{filteredReports.length === 1
								? "publicação encontrada"
								: "publicações encontradas"}
						</p>
					</div>

					{filteredReports.length > 0 ? (
						<div className="mt-6 grid gap-6 lg:grid-cols-2">
							{filteredReports.map((report) => (
								<Card key={report.id} className="flex h-full flex-col p-7">
									<div className="flex items-start justify-between gap-5">
										<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-brand-blue">
											<FileText size={23} />
										</div>

										<Badge variant="info">{report.category}</Badge>
									</div>

									<div className="mt-6 flex-1">
										<h3 className="text-xl font-semibold leading-snug text-slate-950">
											{report.title}
										</h3>

										<p className="mt-3 text-sm leading-6 text-slate-600">
											{report.description}
										</p>
									</div>

									<div className="mt-7 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-slate-100 pt-5 text-sm text-slate-500">
										<span className="inline-flex items-center gap-2">
											<CalendarDays size={16} />

											{report.year}
										</span>

										<span>Publicado em {formatDate(report.publishedAt)}</span>
									</div>

									<div className="mt-6">
										{report.file ? (
											<a
												href={`${import.meta.env.BASE_URL}reports/${report.file}`}
												download
												className="inline-flex items-center gap-2 rounded-lg bg-brand-blue px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-blue focus-visible:ring-offset-2"
											>
												<Download size={17} />
												Baixar PDF
											</a>
										) : (
											<span className="inline-flex items-center gap-2 text-sm font-medium text-slate-400">
												<FileSearch size={17} />
												Documento demonstrativo
											</span>
										)}
									</div>
								</Card>
							))}
						</div>
					) : (
						<Card className="mt-6 px-6 py-16 text-center">
							<div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-slate-500">
								<FileSearch size={22} />
							</div>

							<h3 className="mt-5 font-semibold text-slate-900">
								Nenhuma publicação encontrada
							</h3>

							<p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
								Tente alterar o termo de busca ou selecionar outro ano.
							</p>
						</Card>
					)}
				</section>
			</PageContainer>
		</div>
	);
}
