import axios from 'axios';

export const getAccounts = async () => {
    const response = await axios.get('/api/account');
    return response.data;
};