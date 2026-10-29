import { PageContainer } from "../layout/PageContainer";
import { LoadingState } from "./LoadingState";

// Fallback das rotas carregadas sob demanda: ocupa o lugar da página dentro do
// PublicLayout enquanto o chunk dela chega. Reaproveita o LoadingState para que
// o visual de carregamento continue definido num único lugar.
export function PageLoading() {
	return (
		<PageContainer className="py-16">
			<LoadingState message="Carregando página..." />
		</PageContainer>
	);
}
