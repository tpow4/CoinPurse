import { createSlice, createAsyncThunk, createEntityAdapter, EntityState } from "@reduxjs/toolkit";
import { getInstitutions, createInstitution, CreateInstitutionPayload } from "../../services/institutionService";
import axios from "axios";
import { RootState } from "../store";

export const fetchInstitutions = createAsyncThunk(
    "institutions/fetchInstitutions",
    async (_, thunkAPI) => {
        try {
            const response = await getInstitutions();
            return response;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                return thunkAPI.rejectWithValue(error.response.data);
            }
            else if (error instanceof Error) {
                return thunkAPI.rejectWithValue(error.message);
            }
            return thunkAPI.rejectWithValue("Unknown error");
        }
    }
);

export const createInstitutionThunk = createAsyncThunk(
    "institutions/createInstitution",
    async (data: CreateInstitutionPayload, thunkAPI) => {
        try {
            const response = await createInstitution(data);
            thunkAPI.dispatch(fetchInstitutions());
            return response;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                return thunkAPI.rejectWithValue(error.response.data);
            }
            else if (error instanceof Error) {
                return thunkAPI.rejectWithValue(error.message);
            }
            return thunkAPI.rejectWithValue("Unknown error");
        }
    }
);

export interface Institution {
    id: number;
    name: string;
    description?: string;
}

interface InstitutionsState extends EntityState<Institution, number> {
    status: 'idle' | 'pending' | 'succeeded' | 'rejected';
    error: string | null;
}

const institutionsAdapter = createEntityAdapter<Institution>();

const initialState: InstitutionsState = institutionsAdapter.getInitialState({
    status: 'idle',
    error: null
});

const institutionsSlice = createSlice({
    name: "institutions",
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchInstitutions.pending, (state) => {
                state.status = 'pending';
                state.error = null;
            })
            .addCase(fetchInstitutions.fulfilled, (state, action) => {
                state.status = 'succeeded';
                institutionsAdapter.setAll(state, action.payload);
            })
            .addCase(fetchInstitutions.rejected, (state, action) => {
                state.status = 'rejected';
                state.error = action.payload as string;
            })
            .addCase(createInstitutionThunk.pending, (state) => {
                state.status = 'pending';
                state.error = null;
            })
            .addCase(createInstitutionThunk.fulfilled, (state) => {
                state.status = 'succeeded';
            })
            .addCase(createInstitutionThunk.rejected, (state, action) => {
                state.status = 'rejected';
                state.error = action.payload as string;
            });
    },
});

export default institutionsSlice.reducer;

export const { selectAll: selectAllInstitutions, selectById: selectInstitutionById } =
    institutionsAdapter.getSelectors((state: RootState) => state.institutions);

export const selectInstitutionsStatus = (state: RootState) => state.institutions.status;
export const selectInstitutionsError = (state: RootState) => state.institutions.error;
