import { configureStore } from '@reduxjs/toolkit';
import accountsReducer from './slices/accountsSlice';
import balancesReducer from './slices/balancesSlice';
import periodsReducer from './slices/periodsSlice';
import institutionsReducer from './slices/institutionsSlice';

export const store = configureStore({
    reducer: {
        accounts: accountsReducer,
        balances: balancesReducer,
        periods: periodsReducer,
        institutions: institutionsReducer
    },
});

export type AppStore = typeof store
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
