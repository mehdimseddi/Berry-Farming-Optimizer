// frontend/src/components/AccordionAllocations.tsx
"use client";

import {
    Accordion,
    AccordionItem,
    AccordionTrigger,
    AccordionContent,
} from "@/components/ui/accordion";
import { ITEM_IMAGES } from "@/lib/images";

type SeedType = "plain_spicy" | "very_spicy" | "very_bitter" | "plain_bitter" | "very_sweet" | "plain_sweet";

interface Allocation {
    account_id: string;
    character_name: string | null;
    parent_account_name: string | null;
    plants: Record<string, number>;
    total_plants: number;
    final_seeds: Record<SeedType, number>;
}

interface Props {
    allocations: Allocation[];
}

const PLANT_LABELS: Record<string, string> = {
    leppa: "Leppa",
    cheri: "Cheri",
    pecha: "Pecha",
    strawbst: "Strawbst",
};

const SEED_LABELS: Record<string, string> = {
    plain_spicy: "Plain Spicy",
    very_spicy: "Very Spicy",
    very_bitter: "Very Bitter",
    plain_bitter: "Plain Bitter",
    very_sweet: "Very Sweet",
    plain_sweet: "Plain Sweet",
};

export function AccordionAllocations({ allocations }: Props) {
    const maxPlants = 156;

    if (!allocations.length) {
        return (
            <div className="p-6 text-center text-muted-foreground">
                🌱 No accounts allocated yet.
            </div>
        );
    }

    return (
        <Accordion type="single" collapsible className="space-y-4">
            {allocations.map((alloc) => {
                const usagePercent = (alloc.total_plants / maxPlants) * 100;

                return (
                    <AccordionItem value={alloc.account_id} key={alloc.account_id}>
                        <AccordionTrigger className="hover:no-underline py-3 px-4 bg-background hover:bg-secondary-background transition-colors">
                            <div className="text-left space-y-1 w-full">
                                <h3 className="font-heading">
                                    {alloc.character_name || "Unnamed Account"}
                                </h3>
                                {alloc.parent_account_name && (
                                    <p className="text-sm text-muted-foreground">
                                        Parent: {alloc.parent_account_name}
                                    </p>
                                )}
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {(Object.entries(alloc.plants) as [SeedType, number][]).map(([plant, count]) => (
                                        <div key={plant} className="flex items-center gap-1 bg-white/80 px-2 py-1 rounded-full text-xs font-medium">
                                            <img
                                                src={ITEM_IMAGES[plant]}
                                                alt={PLANT_LABELS[plant]}
                                                className="h-5 w-5 object-contain"
                                            />
                                            <span>{count}</span>
                                        </div>
                                    ))}
                                </div>
                                <div className="text-xs text-muted-foreground mt-1">
                                    {alloc.total_plants} / {maxPlants} slots used
                                </div>
                                <div className="h-1.5 w-full bg-secondary-background rounded-full overflow-hidden border-2 border-border">
                                    <div
                                        className={`h-full ${usagePercent > 90
                                            ? "bg-red-500"
                                            : usagePercent > 70
                                                ? "bg-yellow-500"
                                                : "bg-main"
                                            }`}
                                        style={{ width: `${usagePercent}%` }}
                                    ></div>
                                </div>
                            </div>
                        </AccordionTrigger>

                        <AccordionContent className="px-4 pb-4 space-y-3 bg-secondary-background">
                            <div className="pt-4">
                                <p className="text-sm font-medium mb-2">Final Seed Inventory</p>
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                                    {(Object.entries(alloc.final_seeds) as [SeedType, number][]).map(([seed, amount]) => (
                                        <div key={seed} className="flex items-center gap-2">
                                            <img
                                                src={ITEM_IMAGES[seed]}
                                                alt={SEED_LABELS[seed]}
                                                className="h-4 w-4 object-contain"
                                            />
                                            <span className="capitalize">{SEED_LABELS[seed]}:</span>
                                            <span className="font-medium">{amount}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </AccordionContent>
                    </AccordionItem>
                );
            })}
        </Accordion>
    );
}