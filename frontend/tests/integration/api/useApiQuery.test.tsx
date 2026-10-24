import { act, renderHook, waitFor } from "@testing-library/react";
import { StrictMode } from "react";
import { describe, expect, it, vi } from "vitest";
import { ApiError } from "../../../src/api/errors";
import { useApiQuery } from "../../../src/api/useApiQuery";

interface Deferred<T> {
	promise: Promise<T>;
	resolve: (value: T) => void;
	reject: (reason: unknown) => void;
}

function deferred<T>(): Deferred<T> {
	let resolve!: (value: T) => void;
	let reject!: (reason: unknown) => void;
	const promise = new Promise<T>((res, rej) => {
		resolve = res;
		reject = rej;
	});

	return { promise, resolve, reject };
}

describe("useApiQuery", () => {
	it("vai de loading para success", async () => {
		const fetcher = vi.fn(async () => [{ id: 1 }]);

		const { result } = renderHook(() => useApiQuery(fetcher, []));

		expect(result.current.status).toBe("loading");

		await waitFor(() => expect(result.current.status).toBe("success"));

		expect(result.current.data).toEqual([{ id: 1 }]);
		expect(result.current.error).toBeNull();
	});

	it("marca empty quando o array vem vazio", async () => {
		const { result } = renderHook(() =>
			useApiQuery(async () => [] as number[], []),
		);

		await waitFor(() => expect(result.current.status).toBe("empty"));

		expect(result.current.data).toEqual([]);
	});

	it("aceita isEmpty customizado", async () => {
		const { result } = renderHook(() =>
			useApiQuery(async () => ({ items: [] as number[] }), [], {
				isEmpty: (data) => data.items.length === 0,
			}),
		);

		await waitFor(() => expect(result.current.status).toBe("empty"));
	});

	it("não trata objeto como vazio por padrão", async () => {
		const { result } = renderHook(() => useApiQuery(async () => ({}), []));

		await waitFor(() => expect(result.current.status).toBe("success"));
	});

	it("expõe o ApiError no estado error", async () => {
		const apiError = new ApiError({
			status: 500,
			code: "internal_error",
			detail: "Falhou.",
		});

		const { result } = renderHook(() =>
			useApiQuery(async () => Promise.reject(apiError), []),
		);

		await waitFor(() => expect(result.current.status).toBe("error"));

		expect(result.current.error).toBe(apiError);
		expect(result.current.data).toBeNull();
	});

	it("cancela a requisição ao desmontar", async () => {
		const pending = deferred<number[]>();
		let received: AbortSignal | undefined;

		const { unmount } = renderHook(() =>
			useApiQuery((signal) => {
				received = signal;

				return pending.promise;
			}, []),
		);

		expect(received?.aborted).toBe(false);

		unmount();

		expect(received?.aborted).toBe(true);
	});

	it("ignora a resposta atrasada de uma requisição cancelada", async () => {
		const first = deferred<string>();
		const second = deferred<string>();
		const responses = [first, second];
		let call = 0;

		const { result, rerender } = renderHook(
			({ id }) => useApiQuery(() => responses[call++].promise, [id]),
			{ initialProps: { id: 1 } },
		);

		rerender({ id: 2 });

		await act(async () => {
			second.resolve("segunda");
		});
		await waitFor(() => expect(result.current.data).toBe("segunda"));

		await act(async () => {
			first.resolve("primeira");
		});

		expect(result.current.data).toBe("segunda");
		expect(result.current.status).toBe("success");
	});

	it("refaz a busca quando as deps mudam", async () => {
		const fetcher = vi.fn(async () => ["x"]);

		const { rerender } = renderHook(
			({ year }) => useApiQuery(fetcher, [year]),
			{
				initialProps: { year: 2024 },
			},
		);

		await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(1));

		rerender({ year: 2025 });

		await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
	});

	it("refetch busca de novo e se recupera de um erro", async () => {
		const fetcher = vi
			.fn<() => Promise<string[]>>()
			.mockRejectedValueOnce(
				new ApiError({ status: 0, code: "network_error", detail: "Sem rede." }),
			)
			.mockResolvedValueOnce(["ok"]);

		const { result } = renderHook(() => useApiQuery(fetcher, []));

		await waitFor(() => expect(result.current.status).toBe("error"));

		act(() => {
			result.current.refetch();
		});

		await waitFor(() => expect(result.current.status).toBe("success"));

		expect(fetcher).toHaveBeenCalledTimes(2);
		expect(result.current.data).toEqual(["ok"]);
		expect(result.current.error).toBeNull();
	});

	it("completa a busca em StrictMode (montagem dupla)", async () => {
		const { result } = renderHook(() => useApiQuery(async () => ["ok"], []), {
			wrapper: StrictMode,
		});

		await waitFor(() => expect(result.current.status).toBe("success"));

		expect(result.current.data).toEqual(["ok"]);
	});
});
