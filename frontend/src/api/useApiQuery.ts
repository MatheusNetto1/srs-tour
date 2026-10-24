import {
	type DependencyList,
	useCallback,
	useEffect,
	useRef,
	useState,
} from "react";
import { ApiError } from "./errors";

export type QueryStatus = "loading" | "error" | "empty" | "success";

interface QueryState<T> {
	status: QueryStatus;
	data: T | null;
	error: ApiError | null;
}

interface UseApiQueryOptions<T> {
	isEmpty?: (data: T) => boolean;
}

export interface UseApiQueryResult<T> extends QueryState<T> {
	refetch: () => void;
}

function defaultIsEmpty(data: unknown): boolean {
	return Array.isArray(data) && data.length === 0;
}

function sameDeps(a: DependencyList, b: DependencyList): boolean {
	return a.length === b.length && a.every((item, i) => Object.is(item, b[i]));
}

function toApiError(error: unknown): ApiError {
	return error instanceof ApiError ? error : ApiError.internal(0);
}

/**
 * Busca dados ao montar e sempre que `deps` mudar. Cancela a requisição
 * anterior (e a do desmonte) e ignora respostas que chegam atrasadas.
 */
export function useApiQuery<T>(
	fetcher: (signal: AbortSignal) => Promise<T>,
	deps: DependencyList,
	{ isEmpty = defaultIsEmpty }: UseApiQueryOptions<T> = {},
): UseApiQueryResult<T> {
	const [state, setState] = useState<QueryState<T>>({
		status: "loading",
		data: null,
		error: null,
	});
	const latest = useRef({ fetcher, isEmpty });
	const controller = useRef<AbortController | null>(null);
	const lastDeps = useRef<DependencyList | null>(null);

	// Declarado antes do efeito de busca: roda primeiro a cada render.
	useEffect(() => {
		latest.current = { fetcher, isEmpty };
	});

	const run = useCallback(() => {
		controller.current?.abort();

		const current = new AbortController();
		controller.current = current;

		setState((previous) => ({ ...previous, status: "loading", error: null }));

		latest.current.fetcher(current.signal).then(
			(data) => {
				if (current.signal.aborted) return;

				setState({
					status: latest.current.isEmpty(data) ? "empty" : "success",
					data,
					error: null,
				});
			},
			(error: unknown) => {
				if (current.signal.aborted) return;

				setState({ status: "error", data: null, error: toApiError(error) });
			},
		);
	}, []);

	// Sem array de dependências de propósito: `deps` é dinâmico, então a
	// comparação (a mesma do React) é feita aqui. Busca na montagem e quando
	// `deps` muda.
	useEffect(() => {
		if (lastDeps.current && sameDeps(lastDeps.current, deps)) return;

		lastDeps.current = deps;
		run();
	});

	// Cancela ao desmontar. Zerar `lastDeps` faz o StrictMode (cleanup seguido
	// de nova montagem) buscar de novo em vez de ficar com a requisição abortada.
	useEffect(
		() => () => {
			controller.current?.abort();
			lastDeps.current = null;
		},
		[],
	);

	return { ...state, refetch: run };
}
