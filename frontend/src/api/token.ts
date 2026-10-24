const TOKEN_KEY = "srs-tour.token";

// O acesso ao sessionStorage pode lançar (modo privado, storage bloqueado).
export function getToken(): string | null {
	try {
		return sessionStorage.getItem(TOKEN_KEY);
	} catch {
		return null;
	}
}

export function setToken(token: string): void {
	try {
		sessionStorage.setItem(TOKEN_KEY, token);
	} catch {
		// Sem storage, o token não persiste.
	}
}

export function clearToken(): void {
	try {
		sessionStorage.removeItem(TOKEN_KEY);
	} catch {
		// Nada a limpar.
	}
}
