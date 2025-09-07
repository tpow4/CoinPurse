import { createAsyncThunk, createEntityAdapter, createSlice, EntityState } from "@reduxjs/toolkit";
import { getPeriods, Period } from "../../services/periodService";
import { RootState } from "../store";
import axios from "axios";

export type { Period } from "../../services/periodService";

export const fetchPeriods = createAsyncThunk(
    "periods/fetchPeriods",
    async (_, thunkAPI) => {
        try {
            const response = await getPeriods();
            return response;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                return thunkAPI.rejectWithValue(error.response.data);
            }
            if (error instanceof Error) {
                return thunkAPI.rejectWithValue(error.message);
            }
            return thunkAPI.rejectWithValue("Unknown error");
        }
    }
);

interface PeriodsState extends EntityState<Period, number> {
    status: 'idle' | 'pending' | 'succeeded' | 'rejected';
    error: string | null;
}

const periodsAdapter = createEntityAdapter<Period>();

const initialState: PeriodsState = periodsAdapter.getInitialState({
    status: 'idle',
    error: null
});

const periodsSlice = createSlice({
    name: "periods",
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchPeriods.pending, (state) => {
                state.status = 'pending'; // Changed from 'idle' to 'pending'
                state.error = null
            })
            .addCase(fetchPeriods.fulfilled, (state, action) => {
                state.status = 'succeeded';
                periodsAdapter.setAll(state, action.payload)
            })
            .addCase(fetchPeriods.rejected, (state, action) => {
                state.status = 'rejected';
                state.error = action.payload as string;
            });
    },
});

export default periodsSlice.reducer;
export const { selectAll: selectAllPeriods, selectById: selectPeriodById } =
    periodsAdapter.getSelectors((state: RootState) => state.periods)

export const selectPeriodsStatus = (state: RootState) => state.periods.status;
export const selectPeriodsError = (state: RootState) => state.periods.error;