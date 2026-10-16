import {
	ArrowRight,
	BarChart3,
	BedDouble,
	BriefcaseBusiness,
	Building2,
	FileText,
	Hotel,
	Users,
} from "lucide-react";
import { Link } from "react-router-dom";

import { PageContainer } from "../../components/layout/PageContainer";
import { Card } from "../../components/ui/Card";

const indicators = [
	{
		label: "Meios de hospedagem",
		value: "—",
		icon: Hotel,
	},
	{
		label: "Leitos disponíveis",
		value: "—",
		icon: BedDouble,
	},
	{
		label: "Empresas do setor",
		value: "—",
		icon: Building2,
	},
	{
		label: "Empregos no turismo",
		value: "—",
		icon: BriefcaseBusiness,
	},
];

const resources = [
	{
		title: "Indicadores turísticos",
		description:
			"Consulte dados organizados sobre hospedagem, empresas, empregos e outros indicadores do turismo local.",
		icon: BarChart3,
		to: "/indicadores",
	},
	{
		title: "Dashboard",
		description:
			"Visualize os principais dados do Observatório em gráficos e comparações de leitura rápida.",
		icon: Users,
		to: "/indicadores",
	},
	{
		title: "Relatórios públicos",
		description:
			"Acesse pesquisas e relatórios produzidos pelo Observatório do Turismo para consulta e download.",
		icon: FileText,
		to: "/relatorios",
	},
];

export function Home() {
	return (
		<>
			<section className="bg-brand-gradient text-white">
				<PageContainer
					size="wide"
					className="grid gap-12 py-20 md:py-28 lg:grid-cols-[1.2fr_0.8fr] lg:items-center"
				>
					<div>
						<p className="mb-5 text-sm font-semibold uppercase tracking-[0.2em] text-white/80">
							Observatório do Turismo
						</p>

						<h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
							Dados para compreender e fortalecer o turismo de Santa Rita do
							Sapucaí
						</h1>

						<p className="mt-6 max-w-2xl text-base leading-7 text-white/85 sm:text-lg">
							Consulte indicadores, acompanhe informações do setor e acesse
							pesquisas produzidas pelo Observatório do Turismo do município.
						</p>

						<div className="mt-8 flex flex-wrap gap-4">
							<Link
								to="/indicadores"
								className="inline-flex items-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-semibold text-brand-blue transition hover:bg-slate-100"
							>
								Explorar indicadores
								<ArrowRight size={18} />
							</Link>

							<Link
								to="/relatorios"
								className="inline-flex items-center gap-2 rounded-lg border border-white/40 bg-white/10 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/20"
							>
								Ver relatórios
								<FileText size={18} />
							</Link>
						</div>
					</div>

					<div className="hidden lg:block">
						<div className="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-sm">
							<p className="text-sm font-medium text-white/70">
								Informação pública e organizada
							</p>

							<p className="mt-4 text-2xl font-semibold leading-snug">
								Um ponto de acesso para acompanhar o desenvolvimento do turismo
								no município.
							</p>

							<div className="mt-8 grid grid-cols-2 gap-3">
								<div className="rounded-xl bg-white/10 p-4">
									<BarChart3 />

									<p className="mt-3 text-sm font-medium">Indicadores</p>
								</div>

								<div className="rounded-xl bg-white/10 p-4">
									<FileText />

									<p className="mt-3 text-sm font-medium">Relatórios</p>
								</div>

								<div className="rounded-xl bg-white/10 p-4">
									<Building2 />

									<p className="mt-3 text-sm font-medium">Setor turístico</p>
								</div>

								<div className="rounded-xl bg-white/10 p-4">
									<Users />

									<p className="mt-3 text-sm font-medium">Informação pública</p>
								</div>
							</div>
						</div>
					</div>
				</PageContainer>
			</section>

			<section className="bg-slate-50 py-16 sm:py-20">
				<PageContainer size="wide">
					<div className="max-w-2xl">
						<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-blue">
							Panorama
						</p>

						<h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
							Turismo em números
						</h2>

						<p className="mt-4 leading-7 text-slate-600">
							Principais indicadores do setor turístico de Santa Rita do
							Sapucaí.
						</p>
					</div>

					<div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
						{indicators.map((indicator) => {
							const Icon = indicator.icon;

							return (
								<Card key={indicator.label} className="p-6">
									<div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-brand-blue">
										<Icon size={22} />
									</div>

									<p className="mt-6 text-3xl font-bold text-slate-950">
										{indicator.value}
									</p>

									<p className="mt-2 text-sm text-slate-600">
										{indicator.label}
									</p>
								</Card>
							);
						})}
					</div>

					<p className="mt-5 text-xs text-slate-500">
						Os valores serão exibidos conforme os dados oficiais forem
						disponibilizados na plataforma.
					</p>
				</PageContainer>
			</section>

			<section className="bg-white py-16 sm:py-20">
				<PageContainer size="wide">
					<div className="max-w-2xl">
						<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-purple">
							Explore
						</p>

						<h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
							Explore o Observatório
						</h2>

						<p className="mt-4 leading-7 text-slate-600">
							Encontre informações públicas sobre o turismo local de forma
							simples e organizada.
						</p>
					</div>

					<div className="mt-10 grid gap-6 md:grid-cols-3">
						{resources.map((resource) => {
							const Icon = resource.icon;

							return (
								<Link key={resource.title} to={resource.to} className="group">
									<Card className="h-full p-7 transition duration-200 group-hover:-translate-y-1 group-hover:shadow-md">
										<div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-gradient text-white">
											<Icon size={23} />
										</div>

										<h3 className="mt-6 text-xl font-semibold text-slate-950">
											{resource.title}
										</h3>

										<p className="mt-3 text-sm leading-6 text-slate-600">
											{resource.description}
										</p>

										<span className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-brand-blue">
											Acessar
											<ArrowRight
												size={16}
												className="transition-transform group-hover:translate-x-1"
											/>
										</span>
									</Card>
								</Link>
							);
						})}
					</div>
				</PageContainer>
			</section>

			<section className="bg-slate-50 py-16 sm:py-20">
				<PageContainer
					size="wide"
					className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center"
				>
					<div>
						<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-magenta">
							Conheça
						</p>

						<h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
							Sobre o Observatório
						</h2>

						<p className="mt-5 max-w-2xl leading-7 text-slate-600">
							O Observatório do Turismo de Santa Rita do Sapucaí reúne e
							organiza informações sobre a atividade turística do município,
							contribuindo para o acompanhamento do setor e para decisões
							baseadas em dados.
						</p>

						<Link
							to="/sobre"
							className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-brand-blue"
						>
							Conhecer o Observatório
							<ArrowRight size={16} />
						</Link>
					</div>

					<Card className="p-8">
						<p className="text-sm font-semibold text-slate-950">
							Para quem são esses dados?
						</p>

						<div className="mt-6 grid gap-4 sm:grid-cols-2">
							{[
								"Gestores públicos",
								"Empreendedores",
								"Pesquisadores",
								"População em geral",
							].map((audience) => (
								<div
									key={audience}
									className="rounded-xl bg-slate-50 px-4 py-4 text-sm font-medium text-slate-700"
								>
									{audience}
								</div>
							))}
						</div>
					</Card>
				</PageContainer>
			</section>
		</>
	);
}
