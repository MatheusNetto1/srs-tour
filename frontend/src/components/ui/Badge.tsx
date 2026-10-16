import type { ReactNode } from "react";

type BadgeVariant = "published" | "draft" | "info";

interface BadgeProps {
	children: ReactNode;
	variant?: BadgeVariant;
}

const variants: Record<BadgeVariant, string> = {
	published: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
	draft: "bg-slate-100 text-slate-600 ring-slate-500/20",
	info: "bg-blue-50 text-brand-blue ring-brand-blue/20",
};

export function Badge({ children, variant = "info" }: BadgeProps) {
	return (
		<span
			className={[
				"inline-flex items-center rounded-full px-2.5 py-1",
				"text-xs font-medium ring-1 ring-inset",
				variants[variant],
			].join(" ")}
		>
			{children}
		</span>
	);
}
