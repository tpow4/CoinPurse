import { createAsyncThunk, createEntityAdapter, createSlice, EntityState } from "@reduxjs/toolkit";
import axios from "axios";
import { getBalances } from "../../services/balanceService";
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
            else if (error instanceof Error) {
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
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchBalances.pending, (state) => {
                state.status = 'idle';
                state.error = null
            })
            .addCase(fetchBalances.fulfilled, (state, action) => {
                state.status = 'succeeded';
                balancesAdapter.setAll(state, action.payload)
            })
            .addCase(fetchBalances.rejected, (state, action) => {
                state.status = 'rejected'
                state.error = action.payload as string;
            });
    },
});

export default balancesSlice.reducer;

export const { selectAll: selectAllBalances, selectById: selectBalanceById } = 
    balancesAdapter.getSelectors((state: RootState) => state.balances);

export const selectBalancesStatus = (state: RootState) => state.balances.status;
export const selectBalancesError = (state: RootState) => state.balances.error