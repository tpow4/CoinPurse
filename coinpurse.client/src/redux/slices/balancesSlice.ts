import { createAsyncThunk, createEntityAdapter, createSlice, EntityState } from "@reduxjs/toolkit";
import axios from "axios";
import { getBalances } from "../../services/balanceService";

export const fetchAccounts = createAsyncThunk(
    "account/fetchAccounts",
    async (_, thunkAPI) => {
        try {
            const response = await getBalances();
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

interface Balance {
    accountId: number;
    periodId: number;
    balance: number;
}

interface BalancesState extends EntityState<Balance, string> {
    status: 'idle' | 'pending' | 'succeeded' | 'rejected';
    error: string | null;
}

const balancesAdapter = createEntityAdapter({
    selectId: (balance: Balance) => `${balance.accountId}-${balance.periodId}` as string,
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
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchAccounts.pending, (state) => {
                state.status = 'idle';
                state.error = null
            })
            .addCase(fetchAccounts.fulfilled, (state, action) => {
                state.status = 'succeeded';
                balancesAdapter.setAll(state, action.payload)
            })
            .addCase(fetchAccounts.rejected, (state, action) => {
                state.status = 'rejected'
                state.error = action.payload as string;
            });
    },
});

export default balancesSlice.reducer;