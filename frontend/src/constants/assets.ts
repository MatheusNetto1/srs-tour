const baseUrl = import.meta.env.BASE_URL;

export const logos = {
	observatorio: {
		black: `${baseUrl}logos/observatorio/Logo_OT_preto.png`,
		white: `${baseUrl}logos/observatorio/Logo_OT_branco.png`,
		pink: `${baseUrl}logos/observatorio/Logo_OT_rosa.png`,
	},

	santaRita: {
		black: `${baseUrl}logos/santa-rita/Descritivo(PT)_Preto.png`,
		white: `${baseUrl}logos/santa-rita/Descritivo(PT)_Branco.png`,
	},

	comtur: {
		black: `${baseUrl}logos/comtur/Logo_COMTUR_2025_preto.png`,
		white: `${baseUrl}logos/comtur/Logo_COMTUR_2025_branco.png`,
		principal: `${baseUrl}logos/comtur/Logo_COMTUR_2025_principal.png`,
	},

	smcelt: {
		black: `${baseUrl}logos/smcelt/Logo_SMCELT_preto_semfundo.png`,
		white: `${baseUrl}logos/smcelt/Logo_SMCELT_branco_semfundo.png`,
		principal: `${baseUrl}logos/smcelt/Logo_SMCELT_principal_semfundo.png`,
	},

	caminhosMantiqueira: {
		principal: `${baseUrl}logos/caminhos-mantiqueira/Circuito.png`,
		white: `${baseUrl}logos/caminhos-mantiqueira/Circuito_branco.png`,
		gray: `${baseUrl}logos/caminhos-mantiqueira/Circuito_cinza.png`,
	},

	minas: {
		principal: `${baseUrl}logos/minas/marcaminas.png`,
		white: `${baseUrl}logos/minas/marcaminas_Branco.png`,
	},
} as const;
