import { createAsyncThunk, createEntityAdapter, createSlice, EntityState } from "@reduxjs/toolkit";
import { getPeriods, createPeriod, getOrCreatePeriodForMonth, getPeriodForDate, Period, CreatePeriod } from "../../services/periodService";
import { RootState } from "../store";
import axios from "axios";

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

export const createPeriodThunk = createAsyncThunk(
    "periods/createPeriod",
    async (period: CreatePeriod, thunkAPI) => {
        try {
            const response = await createPeriod(period);
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

export const createPeriodForMonth = createAsyncThunk(
    "periods/createPeriodForMonth",
    async ({ year, month }: { year: number; month: number }, thunkAPI) => {
        try {
            const response = await getOrCreatePeriodForMonth(year, month);
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

export const findPeriodForDate = createAsyncThunk(
    "periods/findPeriodForDate",
    async (date: Date, thunkAPI) => {
        try {
            const response = await getPeriodForDate(date);
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
    createStatus: 'idle' | 'pending' | 'succeeded' | 'rejected';
    createError: string | null;
}

const periodsAdapter = createEntityAdapter<Period>();

const initialState: PeriodsState = periodsAdapter.getInitialState({
    status: 'idle',
    error: null,
    createStatus: 'idle',
    createError: null
});

const periodsSlice = createSlice({
    name: "periods",
    initialState,
    reducers: {
        clearCreateStatus: (state) => {
            state.createStatus = 'idle';
            state.createError = null;
        },
        clearPeriodsError: (state) => {
            state.error = null;
        }
    },
    extraReducers: (builder) => {
        builder
            // Fetch periods
            .addCase(fetchPeriods.pending, (state) => {
                state.status = 'pending';
                state.error = null;
            })
            .addCase(fetchPeriods.fulfilled, (state, action) => {
                state.status = 'succeeded';
                periodsAdapter.setAll(state, action.payload);
            })
            .addCase(fetchPeriods.rejected, (state, action) => {
                state.status = 'rejected';
                state.error = action.payload as string;
            })
            // Create period
            .addCase(createPeriodThunk.pending, (state) => {
                state.createStatus = 'pending';
                state.createError = null;
            })
            .addCase(createPeriodThunk.fulfilled, (state, action) => {
                state.createStatus = 'succeeded';
                periodsAdapter.addOne(state, action.payload);
            })
            .addCase(createPeriodThunk.rejected, (state, action) => {
                state.createStatus = 'rejected';
                state.createError = action.payload as string;
            })
            // Create period for month
            .addCase(createPeriodForMonth.pending, (state) => {
                state.createStatus = 'pending';
                state.createError = null;
            })
            .addCase(createPeriodForMonth.fulfilled, (state, action) => {
                state.createStatus = 'succeeded';
                // Add the new period to our store (or update if it already exists)
                periodsAdapter.upsertOne(state, action.payload);
            })
            .addCase(createPeriodForMonth.rejected, (state, action) => {
                state.createStatus = 'rejected';
                state.createError = action.payload as string;
            })
            // Find period for date
            .addCase(findPeriodForDate.fulfilled, (state, action) => {
                // If a period was found, add it to our store
                if (action.payload) {
                    periodsAdapter.upsertOne(state, action.payload);
                }
            });
    },
});

export const { clearCreateStatus, clearPeriodsError } = periodsSlice.actions;

export default periodsSlice.reducer;
export const { selectAll: selectAllPeriods, selectById: selectPeriodById } =
    periodsAdapter.getSelectors((state: RootState) => state.periods);

export const selectPeriodsStatus = (state: RootState) => state.periods.status;
export const selectPeriodsError = (state: RootState) => state.periods.error;
export const selectCreatePeriodStatus = (state: RootState) => state.periods.createStatus;
export const selectCreatePeriodError = (state: RootState) => state.periods.createError;