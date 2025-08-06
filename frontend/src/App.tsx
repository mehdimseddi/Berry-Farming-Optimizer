import { Button } from "@/components/ui/button";
import { AccountForm } from "./components/AccountForm";
import { AccountsTable } from "./components/AccountsTable";
import { OptimizationResults } from "./components/OptimizationResults";
import { api } from "./lib/api";
import { useEffect, useState } from "react";
import { Toaster } from "@/components/ui/sonner"

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [editingAccount, setEditingAccount] = useState<any>(null);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
    setEditingAccount(null); // Clear editing state
  };

  const handleDeleteAll = async () => {
    if (confirm("Delete all accounts?")) {
      await api.deleteAllAccounts();
      handleRefresh();
    }
  };

  useEffect(() => {
    // Optionally load accounts on mount
  }, [refreshKey]);

  return (
    <>
      <div className="container mx-auto p-6 max-w-5xl space-y-8">
        <h1 className="font-heading text-3xl">🌱 Berry Farming Optimizer</h1>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <AccountForm onAccountSaved={handleRefresh}
              editingAccount={editingAccount}
              onCancelEdit={() => setEditingAccount(null)}
            />
            <Button variant="neutral" onClick={handleDeleteAll}>
              Delete All Accounts
            </Button>
          </div>

          <div>
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