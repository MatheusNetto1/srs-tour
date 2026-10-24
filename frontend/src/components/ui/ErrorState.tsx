import { AlertCircle } from "lucide-react";
import type { ApiError } from "../../api/errors";
import { Button } from "./Button";
import { Card } from "./Card";

interface ErrorStateProps {
	error: ApiError;
	onRetry: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
	return (
		<Card className="flex flex-col items-center gap-4 px-6 py-12 text-center">
			<div role="alert" className="flex flex-col items-center gap-2">
				<AlertCircle className="text-red-600" size={28} aria-hidden="true" />

				<p className="text-sm text-slate-700">{error.detail}</p>
			</div>

			<Button variant="secondary" onClick={onRetry}>
				Tentar novamente
			</Button>
		</Card>
	);
}
