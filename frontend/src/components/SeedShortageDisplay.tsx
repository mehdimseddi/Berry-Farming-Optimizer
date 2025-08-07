import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface Props {
    seedShortage?: {
        plain_spicy: number;
        very_spicy: number;
        very_bitter: number;
        plain_bitter: number;
        very_sweet: number;
        plain_sweet: number;
    };
}

const SEED_LABELS: Record<string, string> = {
    plain_spicy: "Plain Spicy",
    very_spicy: "Very Spicy",
    very_bitter: "Very Bitter",
    plain_bitter: "Plain Bitter",
    very_sweet: "Very Sweet",
    plain_sweet: "Plain Sweet",
};

export function SeedShortageDisplay({ seedShortage }: Props) {
    if (!seedShortage) return null;

    const shortages = Object.entries(seedShortage).filter(([, amount]) => amount > 0);

    if (shortages.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>✅ Seed Status</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-green-600">You have enough seeds to reach your ideal farming goals!</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>⚠️ Seed Shortage</CardTitle>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-muted-foreground mb-3">You're short on these seeds to reach ideal targets:</p>
                <div className="space-y-3">
                    {shortages.map(([seed, amount]) => (
                        <div key={seed} className="space-y-1">
                            <div className="flex justify-between text-sm">
                                <span>{SEED_LABELS[seed]}</span>
                                <span className="font-bold text-red-600">-{amount}</span>
                            </div>
                            <div className="h-2 w-full bg-secondary-background rounded-full overflow-hidden border-2 border-border">
                                <div
                                    className="h-full bg-red-500"
                                    style={{ width: "100%" }}
                                ></div>
                            </div>
                        </div>
                    ))}
                </div>
                <p className="text-xs text-muted-foreground mt-4">
                    Consider farming more of these seeds or adjusting your ideal ratios.
                </p>
            </CardContent>
        </Card>
    );
}