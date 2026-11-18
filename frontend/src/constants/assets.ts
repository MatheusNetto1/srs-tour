const baseUrl = import.meta.env.BASE_URL;

export const logos = {
	observatorio: {
		black: `${baseUrl}logos/observatorio/Logo_OT_preto.png`,
	},

	smcelt: {
		black: `${baseUrl}logos/smcelt/Logo_SMCELT_preto_semfundo.png`,
	},

	comtur: {
		black: `${baseUrl}logos/comtur/Logo_COMTUR_2025_preto.png`,
	},

	santaRita: {
		black: `${baseUrl}logos/santa-rita/descritivo-pt-preto.png`,
	},

	prefeitura: {
		black: `${baseUrl}logos/prefeitura/prefeitura-horizontal-preto.png`,
	},

	caminhosMantiqueira: {
		principal: `${baseUrl}logos/caminhos-mantiqueira/circuito.png`,
	},

	minas: {
		principal: `${baseUrl}logos/minas/marca-minas.png`,
	},
} as const;
