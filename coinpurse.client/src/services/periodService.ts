import axios from 'axios';

export interface Period {
    id: number;
    name: string;
    startDate: string;
    endDate: string;
}

export interface CreatePeriod {
    name: string;
    startDate: string;
    endDate: string;
}

export interface CreatePeriodForMonth {
    year: number;
    month: number;
}

export const getPeriods = async (): Promise<Period[]> => {
    const response = await axios.get('/api/period');
    return response.data;
};

export const createPeriod = async (period: CreatePeriod): Promise<Period> => {
    const response = await axios.post('/api/period', period);
    return response.data;
};

export const getOrCreatePeriodForMonth = async (year: number, month: number): Promise<Period> => {
    const response = await axios.post('/api/period/for-month', { year, month });
    return response.data;
};

export const getPeriodForDate = async (date: Date): Promise<Period | null> => {
    try {
        const response = await axios.get('/api/period/for-date', {
            params: { date: date.toISOString() }
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
            return null;
        }
        throw error;
    }
};