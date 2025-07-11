import axios from 'axios';

export const getBalances = async () => {
    const response = await axios.get('/api/balance');
    return response.data;
};

// Submits an array of balances to the backend
export const submitBalances = async (balances: { accountId: number; periodId: number; amount: number }[]) => {
    const response = await axios.post('/api/balance/bulk', balances);
    return response.data;
};