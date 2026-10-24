import { afterEach, describe, expect, it, vi } from "vitest";
import { clearToken, getToken, setToken } from "../../../src/api/token";

describe("token", () => {
	afterEach(() => {
		vi.restoreAllMocks();
		sessionStorage.clear();
	});

	it("não tem token por padrão", () => {
		expect(getToken()).toBeNull();
	});

	it("grava e lê o token na chave srs-tour.token", () => {
		setToken("abc");

		expect(getToken()).toBe("abc");
		expect(sessionStorage.getItem("srs-tour.token")).toBe("abc");
	});

	it("remove o token", () => {
		setToken("abc");
		clearToken();

		expect(getToken()).toBeNull();
	});

	it("não lança quando o sessionStorage está indisponível", () => {
		const unavailable = () => {
			throw new DOMException("Acesso negado", "SecurityError");
		};

		vi.spyOn(Storage.prototype, "getItem").mockImplementation(unavailable);
		vi.spyOn(Storage.prototype, "setItem").mockImplementation(unavailable);
		vi.spyOn(Storage.prototype, "removeItem").mockImplementation(unavailable);

		expect(() => setToken("abc")).not.toThrow();
		expect(getToken()).toBeNull();
		expect(() => clearToken()).not.toThrow();
	});
});
