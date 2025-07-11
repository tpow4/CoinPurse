import { configureStore } from '@reduxjs/toolkit';
import accountsReducer from './slices/accountsSlice';
import balancesReducer from './slices/balancesSlice';
import periodsReducer from './slices/periodsSlice';

export const store = configureStore({
    reducer: {
        accounts: accountsReducer,
        balances: balancesReducer,
        periods: periodsReducer
    },
});

export type AppStore = typeof store
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
