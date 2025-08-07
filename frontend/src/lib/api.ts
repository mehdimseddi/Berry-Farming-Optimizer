const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Add this interface
interface SeedShortage {
    plain_spicy: number;
    very_spicy: number;
    very_bitter: number;
    plain_bitter: number;
    very_sweet: number;
    plain_sweet: number;
}

// Update the OptimizationResponse
export type OptimizationResult = {
    success: boolean;
    message: string;
    targets?: {
        leppa: number;
        cheri: number;
        pecha: number;
        strawbst: number;
    };
    ideal_targets?: {
        leppa: number;
        cheri: number;
        pecha: number;
        strawbst: number;
    };
    seed_shortage?: SeedShortage;
    allocations?: any[];
    transfers?: any[];
    status_code: number;
};

export const api = {
    async getAccounts() {
        const res = await fetch(`${API_BASE}/accounts/`);
        if (!res.ok) throw new Error('Failed to fetch accounts');
        return await res.json();
    },

    async createAccount(account: {
        character_name?: string;
        parent_account_name?: string;
        seeds: number[];
    }) {
        const res = await fetch(`${API_BASE}/accounts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(account),
        });
        if (!res.ok) throw new Error('Failed to create account');
        return await res.json();
    },

    async updateAccount(id: string, account: any) {
        const res = await fetch(`${API_BASE}/accounts/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(account),
        });
        if (!res.ok) throw new Error('Failed to update account');
        return await res.json();
    },

    async deleteAccount(id: string) {
        const res = await fetch(`${API_BASE}/accounts/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete account');
    },

    async optimize(weight: number = 10000): Promise<OptimizationResult> {
        const res = await fetch(`${API_BASE}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grouping_penalty_weight: weight }),
        });
        if (!res.ok) throw new Error('Optimization failed');
        return await res.json();
    },

    async getLatestOptimization(): Promise<OptimizationResult> {
        const res = await fetch(`${API_BASE}/optimize/latest`);
        if (!res.ok) throw new Error('Failed to fetch latest optimization');
        return await res.json();
    },

    async deleteAllAccounts() {
        const res = await fetch(`${API_BASE}/accounts`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete all accounts');
        return await res.json();
    },
};