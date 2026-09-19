import type { SelectHTMLAttributes } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
	label: string;
}

export function Select({
	label,
	id,
	className = "",
	children,
	...props
}: SelectProps) {
	return (
		<div className="flex flex-col gap-2">
			<label htmlFor={id} className="text-sm font-medium text-slate-700">
				{label}
			</label>

			<select
				id={id}
				className={[
					"rounded-lg border border-slate-300 bg-white px-3 py-2.5",
					"text-sm text-slate-700 shadow-sm",
					"outline-none transition",
					"focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20",
					className,
				].join(" ")}
				{...props}
			>
				{children}
			</select>
		</div>
	);
}
