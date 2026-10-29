import { existsSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

import { logos } from "../../../src/constants/assets";

const publicDir = path.resolve(__dirname, "../../../public");

describe("logos", () => {
	it("aponta apenas para arquivos que existem em public/", () => {
		const urls = Object.values(logos).flatMap((variants) =>
			Object.values(variants),
		);

		for (const url of urls) {
			const file = path.join(publicDir, url.replace(/^\//, ""));

			expect(existsSync(file), url).toBe(true);
		}
	});
});
