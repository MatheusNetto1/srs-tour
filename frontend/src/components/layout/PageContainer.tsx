import type { ReactNode } from "react";

interface PageContainerProps {
	children: ReactNode;
	className?: string;
	size?: "default" | "wide";
}

const sizes = {
	default: "max-w-7xl",
	wide: "max-w-[1440px]",
};

export function PageContainer({
	children,
	className = "",
	size = "default",
}: PageContainerProps) {
	return (
		<div
			className={[
				"mx-auto w-full px-4 sm:px-6 lg:px-8",
				sizes[size],
				className,
			].join(" ")}
		>
			{children}
		</div>
	);
}
