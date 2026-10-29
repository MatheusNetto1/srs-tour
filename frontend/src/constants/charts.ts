// Paleta oficial dos gráficos (identidade visual do Observatório). Os mesmos
// valores existem como tokens `--color-chart-*`/`--color-brand-purple` em
// src/index.css, para uso em classes Tailwind; o Recharts recebe cores como
// string, por isso elas também ficam aqui.
export const chartPalette = [
	"#5fe6e0",
	"#6c5ce0",
	"#27b7fd",
	"#b986ed",
	"#f3b8f7",
	"#fada77",
] as const;

// Cores das séries dos gráficos de Indicadores. A linha usa o azul da marca
// (brand-blue) e as barras o roxo da paleta, como no protótipo.
export const chartColors = {
	line: "#0a4aad",
	bar: chartPalette[1],
} as const;
