import { describe, expect, it } from "vitest";

import { chartColors, chartPalette } from "../../../src/constants/charts";

describe("paleta dos gráficos", () => {
	it("segue a paleta oficial da identidade visual", () => {
		expect(chartPalette).toEqual([
			"#5fe6e0",
			"#6c5ce0",
			"#27b7fd",
			"#b986ed",
			"#f3b8f7",
			"#fada77",
		]);
	});

	it("mantém as cores das séries de Indicadores do protótipo", () => {
		expect(chartColors).toEqual({ line: "#0a4aad", bar: "#6c5ce0" });
	});
});
