import { describe, expect, it } from "vitest";

import { router } from "../../src/routes/router";

describe("router", () => {
	it("registra as rotas públicas", () => {
		const paths = router.routes[0].children?.map((route) => route.path);

		expect(paths).toEqual(["/", "/indicadores", "/relatorios", "/sobre"]);
	});
});
