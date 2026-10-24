import { Loader2 } from "lucide-react";
import { Card } from "./Card";

interface LoadingStateProps {
	message?: string;
}

export function LoadingState({ message = "Carregando..." }: LoadingStateProps) {
	return (
		<Card className="flex items-center justify-center px-6 py-12 text-slate-600">
			<div role="status" className="flex items-center gap-3">
				<Loader2 className="animate-spin" size={20} aria-hidden="true" />

				<span className="text-sm">{message}</span>
			</div>
		</Card>
	);
}
