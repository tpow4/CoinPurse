import { configureStore } from '@reduxjs/toolkit';
import accountsReducer from './slices/accountsSlice';
import balancesReducer from './slices/balancesSlice';

export const store = configureStore({
    reducer: {
        accounts: accountsReducer,
        balances: balancesReducer
    },
});

export type AppStore = typeof store
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
