import { createSlice, createAsyncThunk, createEntityAdapter, EntityState } from "@reduxjs/toolkit";
import { getAccounts } from "../../services/accountService";
import axios from "axios";
import { RootState } from "../store";

export const fetchAccounts = createAsyncThunk(
    "account/fetchAccounts",
    async (_, thunkAPI) => {
        try {
            const response = await getAccounts();
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

export interface Account {
    id: number;
    name: string;
    taxTypeId: number;
    institutionName: string;
    latestBalance: number;
}

interface AccountsState extends EntityState<Account, number> {
    status: 'idle' | 'pending' | 'succeeded' | 'rejected';
    error: string | null;
}

const accountsAdapter = createEntityAdapter<Account>();

const initialState: AccountsState = accountsAdapter.getInitialState({
    status: 'idle',
    error: null
})

const accountsSlice = createSlice({
    name: "accounts",
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
                accountsAdapter.setAll(state, action.payload)
            })
            .addCase(fetchAccounts.rejected, (state, action) => {
                state.status = 'rejected'
                state.error = action.payload as string;
            });
    },
});

export default accountsSlice.reducer;

export const { selectAll: selectAllAccounts, selectById: selectAccountById } =
    accountsAdapter.getSelectors((state: RootState) => state.accounts)

export const selectAccountsStatus = (state: RootState) => state.accounts.status
export const selectAccountsError = (state: RootState) => state.accounts.error