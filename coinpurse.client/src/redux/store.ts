import { configureStore } from '@reduxjs/toolkit';
import accountsReducer from './slices/accountsSlice';

export const store = configureStore({
    reducer: {
        accounts: accountsReducer,
    },
});

export type AppStore = typeof store
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
