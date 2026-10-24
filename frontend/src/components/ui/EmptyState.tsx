import { Inbox } from "lucide-react";
import { Card } from "./Card";

interface EmptyStateProps {
	message?: string;
}

export function EmptyState({
	message = "Nenhum resultado encontrado.",
}: EmptyStateProps) {
	return (
		<Card className="flex flex-col items-center gap-2 px-6 py-12 text-center text-slate-600">
			<Inbox size={28} aria-hidden="true" />

			<p role="status" className="text-sm">
				{message}
			</p>
		</Card>
	);
}
