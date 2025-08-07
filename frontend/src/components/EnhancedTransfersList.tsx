import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight } from 'lucide-react';
import { ITEM_IMAGES } from "@/lib/images";

type SeedType = "plain_spicy" | "very_spicy" | "very_bitter" | "plain_bitter" | "very_sweet" | "plain_sweet";

interface Transfer {
    from_character: string | null;
    to_character: string | null;
    seed_type: SeedType;
    amount: number;
}

interface Props {
    transfers: Transfer[];
}

export function EnhancedTransfersList({ transfers }: Props) {
    if (transfers.length === 0) {
        return (
            <Card>
                <CardContent className="p-6 text-center text-muted-foreground">
                    🎉 No seed transfers needed! All accounts have the seeds they need.
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-3">
            {transfers.map((tx, i) => (
                <Card key={i} className="hover:shadow-md transition-shadow">
                    <CardContent className="flex items-center gap-3">
                        <div className="flex-shrink-0">
                            <img
                                src={ITEM_IMAGES[tx.seed_type]}
                                alt={tx.seed_type}
                                className="h-8 w-8 object-contain"
                            />                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                                <span className="font-medium text-sm">{tx.amount}</span>
                                <span className="capitalize text-xs bg-secondary-background px-2 py-1 rounded-full">
                                    {tx.seed_type.replace('_', ' ')}
                                </span>
                            </div>
                            <div className="flex items-center text-xs text-muted-foreground mt-1">
                                <span>{tx.from_character || "Unknown"}</span>
                                <ArrowRight className="h-3 mx-1" />
                                <span>{tx.to_character || "Unknown"}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}