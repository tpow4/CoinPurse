import axios from 'axios';

export interface CreateAccountDto {
    institutionId: number;
    name: string;
    taxTypeId: number;
}

export interface AccountDto {
    id: number;
    name: string;
    taxTypeId: number;
    institutionName: string;
    isActive: boolean;
    latestBalance?: number;
}

export const createAccount = async (data: CreateAccountDto): Promise<AccountDto> => {
    const response = await axios.post('/api/account', data, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    return response.data;
};

export const getAccounts = async (): Promise<AccountDto[]> => {
    const response = await axios.get('/api/account');
    return response.data;
};

export const getAccount = async (id: number): Promise<AccountDto> => {
    const response = await axios.get(`/api/account/${id}`);
    return response.data;
};

export const updateAccount = async (id: number, data: Partial<CreateAccountDto & { isActive: boolean }>): Promise<AccountDto> => {
    const response = await axios.put(`/api/account/${id}`, data, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    return response.data;
};

export const deleteAccount = async (id: number): Promise<void> => {
    await axios.delete(`/api/account/${id}`);
};