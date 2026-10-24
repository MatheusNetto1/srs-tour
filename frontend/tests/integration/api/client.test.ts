import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { request } from "../../../src/api/client";
import { ApiError } from "../../../src/api/errors";
import { clearToken, setToken } from "../../../src/api/token";

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

function stubFetch(response: Response | Error) {
	const fetchMock = vi.fn(() =>
		response instanceof Response
			? Promise.resolve(response)
			: Promise.reject(response),
	);

	vi.stubGlobal("fetch", fetchMock);

	return fetchMock;
}

function lastCall(fetchMock: ReturnType<typeof stubFetch>) {
	const [url, init] = fetchMock.mock.calls[0] as unknown as [
		string,
		RequestInit,
	];

	return { url, init, headers: init.headers as Record<string, string> };
}

describe("request", () => {
	beforeEach(() => {
		clearToken();
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		clearToken();
	});

	it("faz GET na base da API e devolve o JSON tipado", async () => {
		const fetchMock = stubFetch(jsonResponse([{ id: 1 }]));

		const data = await request<{ id: number }[]>("/indicators");

		expect(data).toEqual([{ id: 1 }]);
		expect(lastCall(fetchMock).url).toBe("/api/v1/indicators");
		expect(lastCall(fetchMock).init.method).toBe("GET");
	});

	it("serializa a query e ignora valores undefined", async () => {
		const fetchMock = stubFetch(jsonResponse([]));

		await request("/reports", {
			query: {
				year: 2025,
				sector: "hotelaria",
				published: false,
				name: undefined,
			},
		});

		expect(lastCall(fetchMock).url).toBe(
			"/api/v1/reports?year=2025&sector=hotelaria&published=false",
		);
	});

	it("não anexa '?' quando a query só tem valores undefined", async () => {
		const fetchMock = stubFetch(jsonResponse([]));

		await request("/reports", { query: { year: undefined } });

		expect(lastCall(fetchMock).url).toBe("/api/v1/reports");
	});

	it("envia o corpo como JSON", async () => {
		const fetchMock = stubFetch(jsonResponse({ id: 1 }, 201));

		await request("/users", { method: "POST", body: { email: "a@b.com" } });

		const { init, headers } = lastCall(fetchMock);

		expect(init.method).toBe("POST");
		expect(init.body).toBe(JSON.stringify({ email: "a@b.com" }));
		expect(headers["Content-Type"]).toBe("application/json");
	});

	it("devolve undefined em 204 sem corpo", async () => {
		stubFetch(new Response(null, { status: 204 }));

		await expect(request("/reports/1", { method: "DELETE" })).resolves.toBe(
			undefined,
		);
	});

	it("anexa o Bearer token quando há token", async () => {
		setToken("abc123");
		const fetchMock = stubFetch(jsonResponse({}));

		await request("/users/me");

		expect(lastCall(fetchMock).headers.Authorization).toBe("Bearer abc123");
	});

	it("não envia Authorization sem token", async () => {
		const fetchMock = stubFetch(jsonResponse({}));

		await request("/indicators");

		expect(lastCall(fetchMock).headers.Authorization).toBeUndefined();
	});

	it("lança ApiError com o envelope de erro", async () => {
		stubFetch(
			jsonResponse(
				{ detail: "Relatório não encontrado.", code: "report.not_found" },
				404,
			),
		);

		const error = await request("/reports/9").catch((e: unknown) => e);

		expect(error).toBeInstanceOf(ApiError);
		expect(error).toMatchObject({
			status: 404,
			code: "report.not_found",
			detail: "Relatório não encontrado.",
		});
	});

	it("transforma falha de rede em ApiError status 0", async () => {
		stubFetch(new TypeError("Failed to fetch"));

		const error = await request("/indicators").catch((e: unknown) => e);

		expect(error).toBeInstanceOf(ApiError);
		expect(error).toMatchObject({ status: 0, code: "network_error" });
	});

	it("repassa o cancelamento sem convertê-lo em ApiError", async () => {
		stubFetch(new DOMException("Aborted", "AbortError"));

		const error = await request("/indicators").catch((e: unknown) => e);

		expect(error).not.toBeInstanceOf(ApiError);
		expect(error).toMatchObject({ name: "AbortError" });
	});

	it("repassa o signal ao fetch", async () => {
		const fetchMock = stubFetch(jsonResponse([]));
		const controller = new AbortController();

		await request("/indicators", { signal: controller.signal });

		expect(lastCall(fetchMock).init.signal).toBe(controller.signal);
	});
});
