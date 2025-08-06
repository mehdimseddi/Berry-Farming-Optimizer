const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

    async getLatestOptimization() {
        const res = await fetch(`${API_BASE}/optimize/latest`);
        if (!res.ok) throw new Error('Failed to fetch latest optimization');
        return await res.json();
    },

    async optimize(weight: number = 10000) {
        const res = await fetch(`${API_BASE}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grouping_penalty_weight: weight }),
        });
        if (!res.ok) throw new Error('Optimization failed');
        return await res.json();
    },

    async deleteAllAccounts() {
        const res = await fetch(`${API_BASE}/accounts`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete all accounts');
        return await res.json();
    },
};