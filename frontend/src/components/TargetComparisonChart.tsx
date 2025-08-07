import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface Props {
    result: {
        targets?: { leppa: number; cheri: number; pecha: number; strawbst: number };
        ideal_targets?: { leppa: number; cheri: number; pecha: number; strawbst: number };
    };
}

const PLANT_LABELS: Record<string, string> = {
    leppa: "Leppa",
    cheri: "Cheri",
    pecha: "Pecha",
    strawbst: "Strawbst",
};

export function TargetComparisonChart({ result }: Props) {
    if (!result.targets || !result.ideal_targets) return null;

    const plants = Object.keys(result.targets) as Array<keyof typeof result.targets>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>🎯 Target vs Ideal Production</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    {plants.map((plant) => {
                        const actual = result.targets![plant];
                        const ideal = result.ideal_targets![plant];
                        const percent = ideal > 0 ? Math.round((actual / ideal) * 100) : 0;

                        return (
                            <div key={plant} className="space-y-1">
                                <div className="flex justify-between text-sm">
                                    <span>{PLANT_LABELS[plant]}</span>
                                    <span>
                                        {actual} / {ideal} ({percent}%)
                                    </span>
                                </div>
                                <div className="h-2 w-full bg-secondary-background rounded-full overflow-hidden border-2 border-border">
                                    <div
                                        className="h-full bg-main transition-all duration-500"
                                        style={{ width: `${percent}%` }}
                                    ></div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}