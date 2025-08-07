import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";

type Account = {
    id: string;
    character_name: string | null;
    parent_account_name: string | null;
    seeds: number[];
};

export function AccountForm({
    onAccountSaved,
    editingAccount,
    onCancelEdit,
}: {
    onAccountSaved: () => void;
    editingAccount: Account | null;
    onCancelEdit: () => void;
}) {
    const isEditing = !!editingAccount;

    // State - will be updated when editingAccount changes
    const [name, setName] = useState("");
    const [parent, setParent] = useState("");
    const [seeds, setSeeds] = useState<number[]>(Array(6).fill(0));

    // 🔁 Effect: Sync form with editingAccount when it changes
    useEffect(() => {
        if (editingAccount) {
            setName(editingAccount.character_name || "");
            setParent(editingAccount.parent_account_name || "");
            setSeeds([...editingAccount.seeds]); // Copy seed array
        } else {
            // Reset form when not editing
            setName("");
            setParent("");
            setSeeds(Array(6).fill(0));
        }
    }, [editingAccount]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (isEditing && editingAccount) {
                await api.updateAccount(editingAccount.id, {
                    character_name: name || undefined,
                    parent_account_name: parent || undefined,
                    seeds: seeds.map((s) => parseInt(s as any) || 0),
                });
                toast.success("Account Updated", {
                    description: `"${name || "Unnamed"}" has been updated.`,
                });
            } else {
                await api.createAccount({
                    character_name: name || undefined,
                    parent_account_name: parent || undefined,
                    seeds: seeds.map((s) => parseInt(s as any) || 0),
                });
                toast.success("Account Added", {
                    description: `"${name || "Unnamed"}" has been added to your farm.`,
                });
            }

            // ✅ Reset form after save
            setName("");
            setParent("");
            setSeeds(Array(6).fill(0));

            // Notify parent to refresh data and clear editing state
            onAccountSaved();
        } catch (err: any) {
            toast.error("Uh oh! Something went wrong.", {
                description: err.message || "Failed to save account.",
            });
        }
    };

    const handleCancel = () => {
        // ✅ Reset form
        setName("");
        setParent("");
        setSeeds(Array(6).fill(0));
        // Notify parent to exit edit mode
        onCancelEdit();
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="font-heading text-lg">
                {isEditing ? `Editing: ${editingAccount?.character_name || "Unnamed"}` : "Add New Account"}
            </h3>

            <div>
                <Label>Character Name</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
                <Label>Parent Account (Optional)</Label>
                <Input value={parent} onChange={(e) => setParent(e.target.value)} />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-2 gap-y-1">
                {["Plain Spicy", "Very Spicy", "Very Bitter", "Plain Bitter", "Very Sweet", "Plain Sweet"].map(
                    (label, i) => (
                        <div key={i} className="flex flex-col">
                            <Label className="text-xs font-medium">{label}</Label>
                            <Input
                                type="number"
                                value={seeds[i]}
                                onChange={(e) => {
                                    const newSeeds = [...seeds];
                                    newSeeds[i] = e.target.value === "" ? 0 : parseInt(e.target.value) || 0;
                                    setSeeds(newSeeds);
                                }}
                                min="0"
                            />
                        </div>
                    )
                )}
            </div>

            <div className="flex gap-2">
                <Button type="submit">{isEditing ? "Update Account" : "Add Account"}</Button>
                {isEditing && (
                    <Button type="button" variant="neutral" onClick={handleCancel}>
                        Cancel
                    </Button>
                )}
            </div>
        </form>
    );
}