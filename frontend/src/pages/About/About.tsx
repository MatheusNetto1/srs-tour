import {
	BarChart3,
	Building2,
	Database,
	FileText,
	Landmark,
	RefreshCw,
	Search,
	Store,
	Users,
} from "lucide-react";

import { PageContainer } from "../../components/layout/PageContainer";
import { Card } from "../../components/ui/Card";
import { logos } from "../../constants/assets";

const audiences = [
	{
		title: "Gestores públicos",
		description:
			"Informações organizadas para apoiar o acompanhamento da atividade turística e o planejamento de políticas públicas.",
		icon: Landmark,
	},
	{
		title: "Empreendedores",
		description:
			"Dados que ajudam a compreender características e transformações do setor turístico local.",
		icon: Store,
	},
	{
		title: "Pesquisadores",
		description:
			"Indicadores, pesquisas e relatórios reunidos em um ponto de acesso para consulta e análise.",
		icon: Search,
	},
	{
		title: "População",
		description:
			"Acesso público e simplificado a informações sobre a atividade turística de Santa Rita do Sapucaí.",
		icon: Users,
	},
];

const information = [
	{
		title: "Meios de hospedagem",
		description:
			"Informações relacionadas aos estabelecimentos de hospedagem e à capacidade disponível no município.",
		icon: Building2,
	},
	{
		title: "Empresas e empregos",
		description:
			"Indicadores relacionados aos empreendimentos e à atividade econômica vinculada ao turismo.",
		icon: Store,
	},
	{
		title: "Fluxo de visitantes",
		description:
			"Informações e pesquisas destinadas a compreender a movimentação e o perfil dos visitantes.",
		icon: Users,
	},
	{
		title: "Pesquisas e relatórios",
		description:
			"Publicações produzidas a partir do acompanhamento e das pesquisas realizadas pelo Observatório.",
		icon: FileText,
	},
];

export function About() {
	return (
		<div className="bg-slate-50">
			<section className="border-b border-slate-200 bg-white">
				<PageContainer size="wide" className="py-14">
					<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-blue">
						Institucional
					</p>

					<h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950">
						Sobre o Observatório
					</h1>

					<p className="mt-4 max-w-3xl leading-7 text-slate-600">
						Conheça o Observatório do Turismo de Santa Rita do Sapucaí e a
						proposta desta plataforma para organizar e ampliar o acesso às
						informações sobre a atividade turística do município.
					</p>
				</PageContainer>
			</section>

			<section className="bg-slate-50 py-16 sm:py-20">
				<PageContainer
					size="wide"
					className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center"
				>
					<div>
						<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-purple">
							O Observatório
						</p>

						<h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
							Informação para compreender o turismo local
						</h2>

						<div className="mt-6 max-w-3xl space-y-4 leading-7 text-slate-600">
							<p>
								O Observatório do Turismo de Santa Rita do Sapucaí reúne e
								organiza informações relacionadas à atividade turística do
								município.
							</p>

							<p>
								Entre as informações acompanhadas estão dados sobre meios de
								hospedagem, leitos, empresas, empregos, fluxo de visitantes e
								pesquisas relacionadas ao perfil do turista.
							</p>

							<p>
								A organização dessas informações contribui para o acompanhamento
								do setor e amplia as possibilidades de consulta por gestores,
								empreendedores, pesquisadores e pela população.
							</p>
						</div>
					</div>

					<Card className="overflow-hidden">
						<div className="bg-brand-gradient p-8 text-white sm:p-10">
							<div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/15">
								<Database size={24} />
							</div>

							<p className="mt-7 text-sm font-medium text-white/70">
								Observatório do Turismo
							</p>

							<p className="mt-3 text-2xl font-semibold leading-snug">
								Dados organizados para acompanhar o desenvolvimento da atividade
								turística de Santa Rita do Sapucaí.
							</p>
						</div>

						<div className="grid gap-4 p-8 sm:grid-cols-2">
							<div>
								<BarChart3 size={20} className="text-brand-blue" />

								<p className="mt-3 text-sm font-semibold text-slate-900">
									Indicadores
								</p>

								<p className="mt-1 text-sm leading-6 text-slate-500">
									Informações estruturadas sobre o setor.
								</p>
							</div>

							<div>
								<FileText size={20} className="text-brand-purple" />

								<p className="mt-3 text-sm font-semibold text-slate-900">
									Publicações
								</p>

								<p className="mt-1 text-sm leading-6 text-slate-500">
									Pesquisas e relatórios para consulta.
								</p>
							</div>
						</div>
					</Card>
				</PageContainer>
			</section>

			<section className="bg-white py-16 sm:py-20">
				<PageContainer size="wide">
					<div className="max-w-3xl">
						<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-blue">
							A plataforma
						</p>

						<h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
							Por que organizar essas informações?
						</h2>

						<p className="mt-5 leading-7 text-slate-600">
							A coleta e o acompanhamento dos dados turísticos são atividades
							realizadas periodicamente. Esta plataforma propõe centralizar
							essas informações e facilitar sua atualização, publicação e
							consulta.
						</p>
					</div>

					<div className="mt-10 grid gap-6 md:grid-cols-3">
						<Card className="p-7">
							<div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-brand-blue">
								<Database size={21} />
							</div>

							<h3 className="mt-6 text-lg font-semibold text-slate-950">
								Centralizar
							</h3>

							<p className="mt-3 text-sm leading-6 text-slate-600">
								Reunir indicadores, pesquisas e publicações relacionadas ao
								turismo em um único ambiente.
							</p>
						</Card>

						<Card className="p-7">
							<div className="flex h-11 w-11 items-center justify-center rounded-xl bg-purple-50 text-brand-purple">
								<RefreshCw size={21} />
							</div>

							<h3 className="mt-6 text-lg font-semibold text-slate-950">
								Atualizar
							</h3>

							<p className="mt-3 text-sm leading-6 text-slate-600">
								Permitir que as informações sejam mantidas e publicadas de
								maneira mais contínua.
							</p>
						</Card>

						<Card className="p-7">
							<div className="flex h-11 w-11 items-center justify-center rounded-xl bg-pink-50 text-brand-magenta">
								<Users size={21} />
							</div>

							<h3 className="mt-6 text-lg font-semibold text-slate-950">
								Democratizar
							</h3>

							<p className="mt-3 text-sm leading-6 text-slate-600">
								Facilitar o acesso público às informações sobre a atividade
								turística do município.
							</p>
						</Card>
					</div>
				</PageContainer>
			</section>

			<section className="bg-slate-50 py-16 sm:py-20">
				<PageContainer size="wide">
					<div className="max-w-3xl">
						<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-purple">
							Informações
						</p>

						<h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
							O que é acompanhado
						</h2>

						<p className="mt-5 leading-7 text-slate-600">
							O Observatório trabalha com diferentes informações relacionadas à
							dinâmica da atividade turística de Santa Rita do Sapucaí.
						</p>
					</div>

					<div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
						{information.map((item) => {
							const Icon = item.icon;

							return (
								<Card key={item.title} className="p-6">
									<div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white text-brand-blue ring-1 ring-slate-200">
										<Icon size={21} />
									</div>

									<h3 className="mt-6 font-semibold text-slate-950">
										{item.title}
									</h3>

									<p className="mt-3 text-sm leading-6 text-slate-600">
										{item.description}
									</p>
								</Card>
							);
						})}
					</div>
				</PageContainer>
			</section>

			<section className="bg-white py-16 sm:py-20">
				<PageContainer size="wide">
					<div className="max-w-3xl">
						<p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-magenta">
							Público
						</p>

						<h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
							Para quem são essas informações?
						</h2>

						<p className="mt-5 leading-7 text-slate-600">
							A plataforma busca tornar as informações do Observatório
							acessíveis a diferentes públicos interessados no turismo e no
							desenvolvimento do município.
						</p>
					</div>

					<div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
						{audiences.map((audience) => {
							const Icon = audience.icon;

							return (
								<Card key={audience.title} className="p-6">
									<div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-brand-blue">
										<Icon size={21} />
									</div>

									<h3 className="mt-6 font-semibold text-slate-950">
										{audience.title}
									</h3>

									<p className="mt-3 text-sm leading-6 text-slate-600">
										{audience.description}
									</p>
								</Card>
							);
						})}
					</div>
				</PageContainer>
			</section>

			<section className="bg-slate-50 py-16 sm:py-20">
				<PageContainer size="wide">
					<Card className="overflow-hidden">
						<div className="grid lg:grid-cols-[0.9fr_1.1fr]">
							<div className="bg-brand-gradient p-8 text-white sm:p-10 lg:p-12">
								<p className="text-sm font-semibold uppercase tracking-[0.18em] text-white/75">
									Realização
								</p>

								<h2 className="mt-4 text-3xl font-bold tracking-tight">
									Uma iniciativa voltada ao turismo de Santa Rita do Sapucaí
								</h2>

								<p className="mt-5 max-w-xl leading-7 text-white/80">
									A plataforma apoia a organização e a divulgação das
									informações produzidas pelo Observatório do Turismo.
								</p>
							</div>

							<div className="p-8 sm:p-10 lg:p-12">
								<p className="text-sm font-semibold text-slate-900">
									Instituições
								</p>

								<p className="mt-2 max-w-xl text-sm leading-6 text-slate-600">
									Identidade institucional associada ao Observatório e à gestão
									municipal do turismo.
								</p>

								<div className="mt-8 flex flex-wrap items-center gap-x-10 gap-y-8">
									<img
										src={logos.observatorio.black}
										alt="Observatório do Turismo de Santa Rita do Sapucaí"
										className="h-16 w-auto object-contain"
									/>

									<img
										src={logos.smcelt.black}
										alt="Secretaria Municipal de Cultura, Esporte, Lazer e Turismo"
										className="h-16 w-auto object-contain"
									/>

									<img
										src={logos.comtur.black}
										alt="Conselho Municipal de Turismo"
										className="h-14 w-auto object-contain"
									/>
								</div>
							</div>
						</div>
					</Card>
				</PageContainer>
			</section>
		</div>
	);
}
