import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export function OptimizationResults() {
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const runOptimization = async () => {
        setLoading(true);
        try {
            const res = await api.optimize(10000);
            setResult(res);
        } catch (err: any) {
            toast.error("Uh oh! Something went wrong.", {
                description: err.message || "Failed to optimize.",
            });
        } finally {
            setLoading(false);
        }
    };

    if (!result) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Optimize Farming</CardTitle>
                </CardHeader>
                <CardContent>
                    <p>Click below to calculate optimal plant allocation and seed transfers.</p>
                </CardContent>
                <CardFooter>
                    <Button onClick={runOptimization} disabled={loading}>
                        {loading ? "Optimizing..." : "Optimize"}
                    </Button>
                </CardFooter>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Optimization Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                <div>
                    <h3 className="font-heading">Targets</h3>
                    <p>
                        Leppa: {result.targets.leppa}, Cheri: {result.targets.cheri}, Pecha: {result.targets.pecha}, Strawbst: {result.targets.strawbst}
                    </p>
                </div>

                <div>
                    <h3 className="font-heading">Allocations</h3>
                    <ul className="text-sm space-y-1">
                        {result.allocations.map((a: any) => (
                            <li key={a.account_id}>
                                {a.character_name || "Unknown"} → {Object.entries(a.plants).map(([k, v]) => `${k}(${v})`).join(", ")}
                            </li>
                        ))}
                    </ul>
                </div>

                <div>
                    <h3 className="font-heading">Transfers</h3>
                    {result.transfers.length === 0 ? (
                        <p>No transfers needed.</p>
                    ) : (
                        <ul className="text-sm space-y-1">
                            {result.transfers.map((t: any, i: number) => (
                                <li key={i}>
                                    {t.amount} {t.seed_type} → {t.to_character} from {t.from_character}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </CardContent>
            <CardFooter>
                <Button variant="reverse" onClick={() => setResult(null)}>
                    Reset
                </Button>
            </CardFooter>
        </Card>
    );
}