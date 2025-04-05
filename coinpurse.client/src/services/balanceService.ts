import axios from 'axios';

export const getBalances = async () => {
    const response = await axios.get('/api/balance');
    return response.data;
};