// src/components/OptimizationResults.tsx

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { TargetComparisonChart } from "./TargetComparisonChart";
import { SeedShortageDisplay } from "./SeedShortageDisplay";
import { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export function OptimizationResults() {
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [groupingPenalty, setGroupingPenalty] = useState<number>(10000); // Default value

    const runOptimization = async () => {
        setLoading(true);
        try {
            const res = await api.optimize(groupingPenalty); // Pass dynamic weight

            if (!res.success) {
                toast.error("Optimization Failed", {
                    description: res.message || "No feasible solution found.",
                });
            }

            setResult(res);
        } catch (err: any) {
            toast.error("Uh oh! Something went wrong.", {
                description: err.message || "Failed to optimize.",
            });
        } finally {
            setLoading(false);
        }
    };

    const viewLatest = async () => {
        setLoading(true);
        try {
            const res = await api.getLatestOptimization();
            if (res.success) {
                setResult(res);
                toast.success("Latest results loaded");
            } else {
                toast.info("No optimization sessions found");
            }
        } catch (err: any) {
            toast.error("Could not load latest results", {
                description: err.message,
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
                <CardContent className="space-y-6">
                    <p>Adjust how strongly the optimizer avoids spreading plants across multiple accounts:</p>

                    <div className="space-y-3">
                        <label className="text-sm font-medium">Grouping Penalty: {groupingPenalty}</label>
                        <Slider
                            value={[groupingPenalty]}
                            onValueChange={(vals) => setGroupingPenalty(vals[0])}
                            min={1}
                            max={50000}
                            step={1000}
                            className="w-full"
                        />
                        <p className="text-xs text-muted-foreground">
                            Higher = fewer accounts used per plant type (more grouped). Lower = more spread out.
                        </p>
                    </div>
                </CardContent>
                <CardFooter className="flex flex-col sm:flex-row gap-3">
                    <Button onClick={runOptimization} disabled={loading} className="w-full">
                        {loading ? "Optimizing..." : "Optimize"}
                    </Button>
                    <Button variant="neutral" onClick={viewLatest} disabled={loading} className="w-full">
                        {loading ? "Loading..." : "View Latest Results"}
                    </Button>
                </CardFooter>
            </Card>
        );
    }

    // Show result (same as before, with success check)
    return (

        <Card>
            <CardHeader>
                <CardTitle>Optimization Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {!result.success ? (
                    <div className="text-sm text-red-600">
                        <p><strong>Optimization Failed:</strong></p>
                        <p>{result.message || "An unknown error occurred."}</p>
                    </div>
                ) : (
                    <>
                        {/* <div>
                            <h3 className="font-heading">Targets</h3>
                            <p>
                                Leppa: {result.targets.leppa},
                                Cheri: {result.targets.cheri},
                                Pecha: {result.targets.pecha},
                                Strawbst: {result.targets.strawbst}
                            </p>
                        </div> */}
                        <TargetComparisonChart result={result} />
                        <SeedShortageDisplay seedShortage={result.seed_shortage} />
                        <div>
                            <h3 className="font-heading">Allocations</h3>
                            {result.allocations && result.allocations.length > 0 ? (
                                <ul className="text-sm space-y-1">
                                    {result.allocations.map((a: any) => (
                                        <li key={a.account_id}>
                                            {a.character_name || "Unknown"} →{" "}
                                            {Object.entries(a.plants)
                                                .map(([k, v]) => `${k}(${v})`)
                                                .join(", ")}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No plants allocated.</p>
                            )}
                        </div>

                        <div>
                            <h3 className="font-heading">Seed Transfers</h3>
                            {result.transfers && result.transfers.length > 0 ? (
                                <ul className="text-sm space-y-1">
                                    {result.transfers.map((t: any, i: number) => (
                                        <li key={i}>
                                            {t.amount} {t.seed_type} → {t.to_character || "Unknown"}
                                            {' '} from {t.from_character || "Unknown"}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No transfers needed.</p>
                            )}
                        </div>
                    </>
                )}
            </CardContent>
            <CardFooter>
                <Button variant="reverse" onClick={() => setResult(null)} className="w-full">
                    Reset
                </Button>
            </CardFooter>
        </Card>
    );
}