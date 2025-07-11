import axios from 'axios';

export interface Period {
    id: number;
    name: string;
    startDate: string;
    endDate: string;
}

export const getPeriods = async (): Promise<Period[]> => {
    const response = await axios.get('/api/period');
    return response.data;
};
