import { createAsyncThunk, createEntityAdapter, createSlice, EntityState, createSelector } from "@reduxjs/toolkit";
import axios from "axios";
import { getBalances, getBalancesByAccountId, submitBalancesForDate, submitBalancesForMonth, CreateBalance } from "../../services/balanceService";
import { RootState } from "../store";

export const fetchBalances = createAsyncThunk(
    "balance/fetchBalances",
    async (_, thunkAPI) => {
        try {
            const response = await getBalances();
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

export const fetchBalancesByAccountId = createAsyncThunk(
    "balance/fetchBalancesByAccountId",
    async (accountId: number, thunkAPI) => {
        try {
            const response = await getBalancesByAccountId(accountId);
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

export const submitBalancesForMonthThunk = createAsyncThunk(
    "balance/submitBalancesForMonth",
    async (
        { 
            balances, 
            year,
            month
        }: { 
            balances: CreateBalance[]; 
            year: number;
            month: number;
        }, 
        thunkAPI
    ) => {
        try {
            const response = await submitBalancesForMonth({
                year,
                month,
                balances
            });
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

export const submitBalancesForDateThunk = createAsyncThunk(
    "balance/submitBalancesForDate",
    async (
        { 
            balances, 
            targetDate
        }: { 
            balances: CreateBalance[]; 
            targetDate: Date;
        }, 
        thunkAPI
    ) => {
        try {
            const response = await submitBalancesForDate({
                targetDate: targetDate.toISOString(),
                balances
            });
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

export interface Balance {
    accountId: number;
    periodId: number;
    amount: number;
}

interface BalancesState extends EntityState<Balance, string> {
    status: 'idle' | 'pending' | 'succeeded' | 'rejected';
    error: string | null;
}

const balancesAdapter = createEntityAdapter({
    selectId: (balance: Balance): string => `${balance.accountId}-${balance.periodId}`,
    sortComparer: (a, b) => {
        if (a.accountId < b.accountId) {
            return -1;
        }
        if (a.accountId > b.accountId) {
            return 1;
        }
        return a.periodId - b.periodId;
    }
});

const initialState: BalancesState = balancesAdapter.getInitialState({
    status: 'idle',
    error: null
})

const balancesSlice = createSlice({
    name: "balances",
    initialState,
    reducers: {
        clearBalancesError: (state) => {
            state.error = null;
        }
    },
    extraReducers: (builder) => {
        builder
            // Submit balances for month
            .addCase(submitBalancesForMonthThunk.pending, (state) => {
                state.status = 'pending';
                state.error = null;
            })
            .addCase(submitBalancesForMonthThunk.fulfilled, (state, action) => {
                state.status = 'succeeded';
                balancesAdapter.upsertMany(state, action.payload);
            })
            .addCase(submitBalancesForMonthThunk.rejected, (state, action) => {
                state.status = 'rejected';
                state.error = action.payload as string;
            })
            // Submit balances for date
            .addCase(submitBalancesForDateThunk.pending, (state) => {
                state.status = 'pending';
                state.error = null;
            })
            .addCase(submitBalancesForDateThunk.fulfilled, (state, action) => {
                state.status = 'succeeded';
                balancesAdapter.upsertMany(state, action.payload);
            })
            .addCase(submitBalancesForDateThunk.rejected, (state, action) => {
                state.status = 'rejected';
                state.error = action.payload as string;
            })
            // Fetch all balances
            .addCase(fetchBalances.pending, (state) => {
                state.status = 'pending';
                state.error = null;
            })
            .addCase(fetchBalances.fulfilled, (state, action) => {
                state.status = 'succeeded';
                balancesAdapter.setAll(state, action.payload);
            })
            .addCase(fetchBalances.rejected, (state, action) => {
                state.status = 'rejected';
                state.error = action.payload as string;
            })
            // Fetch balances by account ID
            .addCase(fetchBalancesByAccountId.fulfilled, (state, action) => {
                // Add/update the fetched balances without changing overall status
                balancesAdapter.upsertMany(state, action.payload);
            });
    },
});

export const { clearBalancesError } = balancesSlice.actions;

export default balancesSlice.reducer;
export const { selectAll: selectAllBalances, selectById: selectBalanceById } =
    balancesAdapter.getSelectors((state: RootState) => state.balances);

export const selectBalancesStatus = (state: RootState) => state.balances.status;
export const selectBalancesError = (state: RootState) => state.balances.error;

// Memoized selector that groups balances by account
export const selectBalancesByAccount = createSelector(
    [selectAllBalances],
    (balances) => {
        const grouped: { [accountId: number]: typeof balances } = {};
        
        balances.forEach(balance => {
            if (!grouped[balance.accountId]) {
                grouped[balance.accountId] = [];
            }
            grouped[balance.accountId].push(balance);
        });
        
        return grouped;
    }
);
