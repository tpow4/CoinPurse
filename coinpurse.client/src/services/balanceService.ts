import axios from 'axios';

export interface Balance {
    accountId: number;
    periodId: number;
    amount: number;
}

export interface CreateBalance {
    accountId: number;
    amount: number;
}

export interface CreateBalancesForMonth {
    year: number;
    month: number;
    balances: CreateBalance[];
}

export interface CreateBalancesForDate {
    targetDate: string; // ISO date string
    balances: CreateBalance[];
}

export const getBalances = async (): Promise<Balance[]> => {
    const response = await axios.get('/api/balance');
    return response.data;
};

export const getBalancesByAccountId = async (accountId: number): Promise<Balance[]> => {
    const response = await axios.get(`/api/balance/${accountId}`);
    return response.data;
};

// Submit balances for a specific month (creates period if needed)
export const submitBalancesForMonth = async (data: CreateBalancesForMonth): Promise<Balance[]> => {
    const response = await axios.post('/api/balance/for-month', data);
    return response.data;
};

// Submit balances for a specific date (creates period if needed)
export const submitBalancesForDate = async (data: CreateBalancesForDate): Promise<Balance[]> => {
    const response = await axios.post('/api/balance/for-date', data);
    return response.data;
};