import { Button } from "@/components/ui/button";
import { AccountForm } from "./components/AccountForm";
import { AccountsTable } from "./components/AccountsTable";
import { OptimizationResults } from "./components/OptimizationResults";
import { api } from "./lib/api";
import { useEffect, useState } from "react";
import { Toaster } from "@/components/ui/sonner"
import { toast } from "sonner";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "./components/ui/alert-dialog";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [editingAccount, setEditingAccount] = useState<any>(null);
  const [deletingAll, setDeletingAll] = useState(false);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
    setEditingAccount(null); // Clear editing state
  };

  const handleDeleteAll = async () => {
    setDeletingAll(false);
    try {
      await api.deleteAllAccounts();
      toast.success("All accounts deleted", {
        description: "Your farm has been reset.",
      });
      handleRefresh();

    } catch (err: any) {
      toast.error("Delete failed", {
        description: err.message || "Failed to delete all accounts.",
      });
    }
  };

  useEffect(() => {
    // Optionally load accounts on mount
  }, [refreshKey]);

  return (
    <>
      <div className="container mx-auto p-6 max-w-5xl space-y-8">
        <h1 className="font-heading text-3xl">🌱 Berry Farming Optimizer</h1>

        <div className="grid md:grid-cols-2 gap-6 sm:gap-8">
          <div className="space-y-6">
            <AccountForm onAccountSaved={handleRefresh}
              editingAccount={editingAccount}
              onCancelEdit={() => setEditingAccount(null)}
            />
            <AlertDialog open={deletingAll} onOpenChange={setDeletingAll}>
              <AlertDialogTrigger asChild>
                <Button variant="neutral">Delete All Accounts</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will <span className="font-bold text-destructive">permanently delete all accounts</span> and their data.
                    This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDeleteAll}>
                    Delete All
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>

          <div className="overflow-x-auto">
            <AccountsTable onRefresh={handleRefresh}
              onEditAccount={setEditingAccount}
            />
          </div>
        </div>

        <div>
          <OptimizationResults />
        </div>
      </div>
      <Toaster />
    </>
  );
}

export default App;