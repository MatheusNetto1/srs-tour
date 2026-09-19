import { Info } from "lucide-react";

interface DemoNoticeProps {
	children?: string;
}

export function DemoNotice({
	children = "Os dados apresentados nesta versão são demonstrativos e serão substituídos pelos dados oficiais do Observatório.",
}: DemoNoticeProps) {
	return (
		<div className="flex gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
			<Info className="mt-0.5 shrink-0" size={18} />

			<p className="leading-6">{children}</p>
		</div>
	);
}
