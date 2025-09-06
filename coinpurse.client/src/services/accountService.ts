import axios from 'axios';

export interface CreateAccountPayload {
    institutionId: string;
    name: string;
    description?: string;
    taxTypeId: string;
    picture?: File | null;
}

export const createAccount = async (data: CreateAccountPayload) => {
    const formData = new FormData();
    formData.append('institutionId', data.institutionId);
    formData.append('name', data.name);
    formData.append('description', data.description || '');
    formData.append('taxTypeId', data.taxTypeId);
    if (data.picture) {
        formData.append('picture', data.picture);
    }
    const response = await axios.post('/api/account', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getAccounts = async () => {
    const response = await axios.get('/api/account');
    return response.data;
};