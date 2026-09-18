import { PageContainer } from "./PageContainer";

export function Footer() {
	return (
		<footer className="mt-auto border-t border-slate-200 bg-white">
			<PageContainer>
				<div className="py-8 text-sm text-slate-600">
					<p>Observatório do Turismo de Santa Rita do Sapucaí</p>

					<p className="mt-2 text-slate-500">
						Projeto desenvolvido em parceria com a Prefeitura de Santa Rita do
						Sapucaí.
					</p>
				</div>
			</PageContainer>
		</footer>
	);
}
