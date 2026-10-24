export interface FieldError {
	field: string;
	code: string;
	message: string;
}

interface ApiErrorInit {
	status: number;
	code: string;
	detail: string;
	errors?: FieldError[];
}

const VALIDATION_DETAIL = "Dados inválidos.";
const VALIDATION_CODE = "validation.failed";
const INTERNAL_DETAIL = "Erro inesperado no servidor. Tente novamente.";
const NETWORK_DETAIL =
	"Não foi possível conectar ao servidor. Verifique sua conexão.";

export class ApiError extends Error {
	status: number;
	code: string;
	detail: string;
	errors: FieldError[];

	constructor({ status, code, detail, errors = [] }: ApiErrorInit) {
		super(detail);
		this.name = "ApiError";
		this.status = status;
		this.code = code;
		this.detail = detail;
		this.errors = errors;
	}

	static network(): ApiError {
		return new ApiError({
			status: 0,
			code: "network_error",
			detail: NETWORK_DETAIL,
		});
	}

	static internal(status: number): ApiError {
		return new ApiError({
			status,
			code: "internal_error",
			detail: INTERNAL_DETAIL,
		});
	}
}

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isFieldError(value: unknown): value is FieldError {
	return (
		isRecord(value) &&
		typeof value.field === "string" &&
		typeof value.code === "string" &&
		typeof value.message === "string"
	);
}

// Formato antigo do 422: detail = [{ loc, msg, type }, ...] (padrão do FastAPI).
function legacyValidationErrors(detail: unknown[]): FieldError[] {
	return detail.filter(isRecord).map((item) => ({
		field: Array.isArray(item.loc) ? item.loc.join(".") : "",
		code: typeof item.type === "string" ? item.type : "",
		message: typeof item.msg === "string" ? item.msg : "",
	}));
}

/**
 * Normaliza o corpo de uma resposta de erro. Aceita o envelope novo
 * (`detail` string + `code` + `errors`) e o formato antigo (`detail` string
 * sem `code`, ou `detail` como lista de erros de validação no 422).
 */
export function normalizeApiError(status: number, body: unknown): ApiError {
	if (!isRecord(body)) {
		return ApiError.internal(status);
	}

	const { detail } = body;

	if (Array.isArray(detail)) {
		return new ApiError({
			status,
			code: VALIDATION_CODE,
			detail: VALIDATION_DETAIL,
			errors: legacyValidationErrors(detail),
		});
	}

	if (typeof detail !== "string") {
		return ApiError.internal(status);
	}

	return new ApiError({
		status,
		code: typeof body.code === "string" ? body.code : `http_${status}`,
		detail,
		errors: Array.isArray(body.errors) ? body.errors.filter(isFieldError) : [],
	});
}

export async function parseApiError(response: Response): Promise<ApiError> {
	let body: unknown;

	try {
		body = JSON.parse(await response.text());
	} catch {
		return ApiError.internal(response.status);
	}

	return normalizeApiError(response.status, body);
}
