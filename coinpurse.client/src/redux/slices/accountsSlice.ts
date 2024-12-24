import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { getAccounts } from "../../services/accountService";
import axios from "axios";

// Thunks
export const fetchAccounts = createAsyncThunk(
    "account/fetchAccounts",
    async (_, thunkAPI) => {
        try {
            const response = await getAccounts();
            return response;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                return thunkAPI.rejectWithValue(error.response.data);
            } else if (error instanceof Error) {
                return thunkAPI.rejectWithValue(error.message);
            }
            return thunkAPI.rejectWithValue("Unknown error");
        }
    }
);

interface Account {
    id: number;
    name: string;
    taxTypeId: number;
    institutionName: string;
    latestBalance: number;
}

interface AccountsState {
    accounts: Account[];
    loading: boolean;
    error: string | null;
}

const initialState: AccountsState = {
    accounts: [],
    loading: false,
    error: null,
};

const accountsSlice = createSlice({
    name: "accounts",
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchAccounts.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchAccounts.fulfilled, (state, action) => {
                state.loading = false;
                state.accounts = action.payload;
            })
            .addCase(fetchAccounts.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload as string;
            });
    },
});

export default accountsSlice.reducer;
