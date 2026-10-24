import { ApiError, parseApiError } from "./errors";
import { getToken } from "./token";

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
type QueryValue = string | number | boolean | undefined;

export interface RequestOptions {
	method?: HttpMethod;
	query?: Record<string, QueryValue>;
	body?: unknown;
	signal?: AbortSignal;
}

function buildUrl(path: string, query?: Record<string, QueryValue>): string {
	const params = new URLSearchParams();

	for (const [key, value] of Object.entries(query ?? {})) {
		if (value !== undefined) {
			params.append(key, String(value));
		}
	}

	const search = params.toString();

	return `${BASE_URL}${path}${search ? `?${search}` : ""}`;
}

function isAbort(error: unknown): boolean {
	return error instanceof DOMException && error.name === "AbortError";
}

/** Único ponto de `fetch` do frontend. */
export async function request<T>(
	path: string,
	{ method = "GET", query, body, signal }: RequestOptions = {},
): Promise<T> {
	const headers: Record<string, string> = { Accept: "application/json" };
	const token = getToken();

	if (token) {
		headers.Authorization = `Bearer ${token}`;
	}

	if (body !== undefined) {
		headers["Content-Type"] = "application/json";
	}

	let response: Response;

	try {
		response = await fetch(buildUrl(path, query), {
			method,
			headers,
			body: body === undefined ? undefined : JSON.stringify(body),
			signal,
		});
	} catch (error) {
		// O cancelamento não é falha de rede: quem cancelou trata.
		throw isAbort(error) ? error : ApiError.network();
	}

	if (!response.ok) {
		throw await parseApiError(response);
	}

	if (response.status === 204) {
		return undefined as T;
	}

	try {
		return (await response.json()) as T;
	} catch (error) {
		throw isAbort(error) ? error : ApiError.internal(response.status);
	}
}
