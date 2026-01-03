import axios from 'axios';
import { Institution } from '../redux/slices/institutionsSlice';

export interface CreateInstitutionPayload {
    name: string;
    description?: string;
}

export const getInstitutions = async (): Promise<Institution[]> => {
    const response = await axios.get('/api/institution');
    return response.data;
};

export const createInstitution = async (data: CreateInstitutionPayload): Promise<Institution> => {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('description', data.description ?? '');

    const response = await axios.post('/api/institution', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};
