// src/components/OptimizationResults.tsx

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { TargetComparisonChart } from "./TargetComparisonChart";
import { SeedShortageDisplay } from "./SeedShortageDisplay";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AccordionAllocations } from "./EnhancedAllocationsTable";
import { EnhancedTransfersList } from "./EnhancedTransfersList";
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
            console.log(JSON.stringify(res, null, 2));
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
                            onValueChange={(vals) => {
                                const snappedValue = Math.round(vals[0] / 1000) * 1000;
                                setGroupingPenalty(snappedValue === 0 ? 1 : snappedValue)
                            }
                            }
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
                    <div className="space-y-6">
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
                        <Tabs defaultValue="allocations" className="w-full">
                            <TabsList className="grid w-full grid-cols-2">
                                <TabsTrigger value="allocations">Plant Allocations</TabsTrigger>
                                <TabsTrigger value="transfers">Seed Transfers</TabsTrigger>
                            </TabsList>

                            <TabsContent value="allocations">
                                <AccordionAllocations allocations={result.allocations} />
                            </TabsContent>

                            <TabsContent value="transfers">
                                <EnhancedTransfersList transfers={result.transfers} />
                            </TabsContent>
                        </Tabs>
                    </div>
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