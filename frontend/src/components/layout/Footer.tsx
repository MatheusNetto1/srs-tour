import { logos } from "../../constants/assets";
import { PageContainer } from "./PageContainer";

export function Footer() {
	return (
		<footer className="mt-auto border-t border-slate-200 bg-white">
			<PageContainer size="wide">
				<div className="grid gap-10 py-10 md:grid-cols-[1fr_auto] md:items-center">
					<div>
						<img
							src={logos.observatorio.black}
							alt="Observatório do Turismo de Santa Rita do Sapucaí"
							className="h-14 w-auto object-contain"
						/>

						<p className="mt-4 max-w-md text-sm leading-6 text-slate-500">
							Informação e dados para apoiar o desenvolvimento do turismo em
							Santa Rita do Sapucaí.
						</p>
					</div>

					<div className="flex flex-wrap items-center gap-6">
						<img
							src={logos.smcelt.black}
							alt="Secretaria Municipal de Cultura, Esporte, Lazer e Turismo"
							className="h-14 w-auto object-contain"
						/>

						<img
							src={logos.comtur.black}
							alt="Conselho Municipal de Turismo"
							className="h-12 w-auto object-contain"
						/>
					</div>
				</div>

				<div className="border-t border-slate-200 py-6">
					<p className="text-xs text-slate-500">
						Observatório do Turismo de Santa Rita do Sapucaí
					</p>
				</div>
			</PageContainer>
		</footer>
	);
}
