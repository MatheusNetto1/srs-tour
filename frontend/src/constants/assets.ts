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
} as const;
