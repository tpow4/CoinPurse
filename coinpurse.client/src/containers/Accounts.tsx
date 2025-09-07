import { useEffect, useMemo } from "react";
import {
    fetchAccounts,
    selectAllAccounts,
} from "../redux/slices/accountsSlice";
import { useAppDispatch, useAppSelector } from "../redux/hooks";
import {
    fetchBalances,
    selectAllBalances,
} from "../redux/slices/balancesSlice";
import {
    fetchPeriods,
} from "../redux/slices/periodsSlice";
import AccountChart from "./AccountChart";
import Grid2 from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';

export default function Accounts() {
    const dispatch = useAppDispatch();
    
    // Test each selector individually
    console.log('About to call selectAllAccounts');
    const accounts = useAppSelector(selectAllAccounts);
    console.log('Accounts:', accounts.length);
    
    console.log('About to call selectAllBalances');
    const balances = useAppSelector(selectAllBalances);
    console.log('Balances:', balances.length);

    useEffect(() => {
        console.log('About to dispatch fetchAccounts');
        dispatch(fetchAccounts());
        console.log('About to dispatch fetchBalances');
        dispatch(fetchBalances());
        console.log('About to dispatch fetchPeriods');
        dispatch(fetchPeriods());
    }, [dispatch]);

    // Temporarily disable the complex computation
    const balancesByAccount = useMemo(() => {
        console.log('Computing balancesByAccount...');
        // Just return empty object for now
        return {};
    }, [accounts, balances]);

    // Temporarily return simple content
    return (
        <div>
            <Typography>Accounts: {accounts.length}</Typography>
            <Typography>Balances: {balances.length}</Typography>
            {/* Comment out the complex rendering for now */}
            {/*
            <Grid2
                container
                spacing={2}
                columns={12}
                sx={{ mb: (theme) => theme.spacing(2) }}
            >
                {accounts.map((account) => (
                    <Grid2 key={account.id} size={{ xs: 12, md: 6 }}>
                        <AccountChart
                            key={account.id}
                            account={account}
                            balances={balancesByAccount[account.id] ?? []}
                        />
                    </Grid2>
                ))}
            </Grid2>
            */}
        </div>
    );
}