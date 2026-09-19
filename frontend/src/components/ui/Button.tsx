import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	children: ReactNode;
	variant?: ButtonVariant;
}

const variants: Record<ButtonVariant, string> = {
	primary:
		"bg-brand-blue text-white hover:bg-blue-800 focus-visible:ring-brand-blue",
	secondary:
		"border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus-visible:ring-slate-400",
	ghost:
		"bg-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-950 focus-visible:ring-slate-400",
	danger: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600",
};

export function Button({
	children,
	variant = "primary",
	className = "",
	type = "button",
	...props
}: ButtonProps) {
	return (
		<button
			type={type}
			className={[
				"inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5",
				"text-sm font-semibold transition-colors",
				"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
				"disabled:pointer-events-none disabled:opacity-50",
				variants[variant],
				className,
			].join(" ")}
			{...props}
		>
			{children}
		</button>
	);
}
