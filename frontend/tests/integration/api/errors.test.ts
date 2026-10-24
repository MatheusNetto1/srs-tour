import { describe, expect, it } from "vitest";
import { ApiError, parseApiError } from "../../../src/api/errors";

function response(body: string, status: number): Response {
	return new Response(body, { status });
}

describe("parseApiError", () => {
	it("aceita o envelope novo com errors de validação", async () => {
		const error = await parseApiError(
			response(
				JSON.stringify({
					detail: "Dados inválidos.",
					code: "validation.failed",
					errors: [
						{
							field: "body.name",
							code: "string_too_short",
							message: "Nome curto demais.",
						},
					],
				}),
				422,
			),
		);

		expect(error).toBeInstanceOf(ApiError);
		expect(error.status).toBe(422);
		expect(error.code).toBe("validation.failed");
		expect(error.detail).toBe("Dados inválidos.");
		expect(error.errors).toEqual([
			{
				field: "body.name",
				code: "string_too_short",
				message: "Nome curto demais.",
			},
		]);
	});

	it("aceita o envelope novo sem errors", async () => {
		const error = await parseApiError(
			response(
				JSON.stringify({ detail: "Acesso negado.", code: "auth.forbidden" }),
				403,
			),
		);

		expect(error.code).toBe("auth.forbidden");
		expect(error.errors).toEqual([]);
	});

	it("aceita o formato antigo com detail string e deriva o code do status", async () => {
		const error = await parseApiError(
			response(JSON.stringify({ detail: "Indicador não encontrado." }), 404),
		);

		expect(error.status).toBe(404);
		expect(error.code).toBe("http_404");
		expect(error.detail).toBe("Indicador não encontrado.");
		expect(error.errors).toEqual([]);
	});

	it("converte o 422 antigo (detail lista) em errors", async () => {
		const error = await parseApiError(
			response(
				JSON.stringify({
					detail: [
						{
							type: "string_too_short",
							loc: ["body", "name"],
							msg: "String should have at least 3 characters",
							input: "a",
						},
						{
							type: "missing",
							loc: ["body", "address", "city"],
							msg: "Field required",
						},
					],
				}),
				422,
			),
		);

		expect(error.status).toBe(422);
		expect(error.code).toBe("validation.failed");
		expect(error.detail).toBe("Dados inválidos.");
		expect(error.errors).toEqual([
			{
				field: "body.name",
				code: "string_too_short",
				message: "String should have at least 3 characters",
			},
			{
				field: "body.address.city",
				code: "missing",
				message: "Field required",
			},
		]);
	});

	it("trata resposta que não é JSON como internal_error", async () => {
		const error = await parseApiError(response("Internal Server Error", 500));

		expect(error.status).toBe(500);
		expect(error.code).toBe("internal_error");
		expect(error.detail).not.toBe("");
	});

	it("trata JSON sem detail utilizável como internal_error", async () => {
		const error = await parseApiError(response(JSON.stringify({ x: 1 }), 502));

		expect(error.status).toBe(502);
		expect(error.code).toBe("internal_error");
	});
});

describe("ApiError.network", () => {
	it("usa status 0 e code network_error", () => {
		const error = ApiError.network();

		expect(error.status).toBe(0);
		expect(error.code).toBe("network_error");
		expect(error).toBeInstanceOf(Error);
	});
});
