import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
    AlertDialog,
    AlertDialogTrigger,
    AlertDialogContent,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogAction,
    AlertDialogCancel,
} from "@/components/ui/alert-dialog";
import { SquarePen, Trash } from 'lucide-react';
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";

type Account = {
    id: string;
    character_name: string | null;
    parent_account_name: string | null;
    seeds: number[];
};

export function AccountsTable({ onRefresh, onEditAccount, }: { onRefresh: () => void; onEditAccount: (account: Account) => void; }) {
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [deletingId, setDeletingId] = useState<string | null>(null);

    useEffect(() => {
        loadAccounts();
    }, [onRefresh]);

    const loadAccounts = async () => {
        try {
            const data = await api.getAccounts();
            setAccounts(data);
        } catch (err: any) {
            toast.error("Uh oh! Something went wrong.", {
                description: err.message || "Failed to save account.",
            });
        }
    };

    const handleDelete = async () => {
        if (!deletingId) return;
        try {
            await api.deleteAccount(deletingId);
            toast.success("Account deleted", {
                description: "The account has been removed from your farm.",
            });
        } catch (err: any) {
            toast.error("Delete failed", {
                description: err.message,
            });
        } finally {
            setDeletingId(null);
            loadAccounts();
            onRefresh();
        }
    };

    return (
        <div className="rounded-base border-2 border-border overflow-hidden">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Parent</TableHead>
                        <TableHead>Spicy Seeds</TableHead>
                        <TableHead>Bitter Seeds</TableHead>
                        <TableHead>Sweet Seeds</TableHead>
                        <TableHead>Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {accounts.map(acc => (
                        <TableRow key={acc.id}>
                            <TableCell>{acc.character_name || "-"}</TableCell>
                            <TableCell>{acc.parent_account_name || "-"}</TableCell>
                            <TableCell>
                                {acc.seeds[0]} / {acc.seeds[1]}
                            </TableCell>
                            <TableCell>
                                {acc.seeds[3]} / {acc.seeds[2]}
                            </TableCell>
                            <TableCell>
                                {acc.seeds[5]} / {acc.seeds[4]}
                            </TableCell>
                            <TableCell>
                                <div className="flex gap-2">
                                    <Button
                                        variant="reverse"
                                        size="icon"
                                        onClick={() =>
                                            onEditAccount(acc)}
                                    >
                                        <SquarePen />
                                    </Button>


                                    {/* Delete Button with AlertDialog */}
                                    <AlertDialog>
                                        <AlertDialogTrigger asChild>
                                            <Button variant="reverse" size="icon" onClick={() => setDeletingId(acc.id)}>
                                                <Trash />
                                            </Button>
                                        </AlertDialogTrigger>
                                        <AlertDialogContent>
                                            <AlertDialogHeader>
                                                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                                <AlertDialogDescription>
                                                    This will permanently delete the account{" "}
                                                    <strong>{acc.character_name || "Unnamed"}</strong>. This action cannot be undone.
                                                </AlertDialogDescription>
                                            </AlertDialogHeader>
                                            <AlertDialogFooter>
                                                <AlertDialogCancel onClick={() => setDeletingId(null)}>
                                                    Cancel
                                                </AlertDialogCancel>
                                                <AlertDialogAction onClick={handleDelete}>
                                                    Delete
                                                </AlertDialogAction>
                                            </AlertDialogFooter>
                                        </AlertDialogContent>
                                    </AlertDialog>
                                </div>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}