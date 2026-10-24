// Gera src/api/schema.d.ts a partir do /openapi.json do backend (exige o
// backend no ar). Em Node, e não direto no package.json, porque o `npm run`
// usa cmd.exe no Windows e não expande `${VAR:-padrão}`.
import { writeFileSync } from "node:fs";
import openapiTS, { astToString } from "openapi-typescript";

try {
	process.loadEnvFile(".env");
} catch {
	// Sem frontend/.env: vale o padrão abaixo.
}

const target = process.env.API_PROXY_TARGET ?? "http://localhost:8000";
const output = "src/api/schema.d.ts";

try {
	const ast = await openapiTS(new URL("/openapi.json", target));
	writeFileSync(output, astToString(ast));
	console.log(`Tipos gerados em ${output} a partir de ${target}/openapi.json`);
} catch (error) {
	console.error(
		`Erro: não foi possível gerar os tipos a partir de ${target}/openapi.json. O backend está no ar? (make up)`,
	);
	console.error(error instanceof Error ? error.message : error);
	process.exit(1);
}
