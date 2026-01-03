import { useEffect, useCallback } from "react";
import {
    fetchAccounts,
    selectAllAccounts,
    selectAccountsStatus
} from "../redux/slices/accountsSlice";
import { useAppDispatch, useAppSelector } from "../redux/hooks";
import {
    fetchBalances,
    selectBalancesByAccount, // ✅ Use the memoized selector
    selectBalancesStatus
} from "../redux/slices/balancesSlice";
import {
    fetchPeriods,
    selectPeriodsStatus
} from "../redux/slices/periodsSlice";
import AccountChart from "./AccountChart";
import Grid2 from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

export default function Accounts() {
    const dispatch = useAppDispatch();
    
    const accountsStatus = useAppSelector(selectAccountsStatus);
    const balancesStatus = useAppSelector(selectBalancesStatus);
    const periodsStatus = useAppSelector(selectPeriodsStatus);
    
    const accounts = useAppSelector(selectAllAccounts);
    const balancesByAccount = useAppSelector(selectBalancesByAccount);

    // Fetch data with status checks
    const fetchData = useCallback(() => {
        if (accountsStatus === 'idle') {
            dispatch(fetchAccounts());
        }
        if (balancesStatus === 'idle') {
            dispatch(fetchBalances());
        }
        if (periodsStatus === 'idle') {
            dispatch(fetchPeriods());
        }
    }, [dispatch, accountsStatus, balancesStatus, periodsStatus]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Loading states
    if (accountsStatus === 'pending' || balancesStatus === 'pending' || periodsStatus === 'pending') {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6">Loading accounts and balances...</Typography>
            </Box>
        );
    }

    // Error states
    if (accountsStatus === 'rejected') {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="error">Failed to load accounts</Typography>
            </Box>
        );
    }

    if (balancesStatus === 'rejected') {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="error">Failed to load balances</Typography>
            </Box>
        );
    }

    // Empty state
    if (accounts.length === 0) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary">
                    No accounts found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Create an account to get started
                </Typography>
            </Box>
        );
    }

    // Calculate total balances for display
    const totalBalances = Object.values(balancesByAccount).flat().length;

    return (
        <Box>
            <Typography variant="h4" gutterBottom>
                Account Balances
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
                {accounts.length} accounts with {totalBalances} balance records
            </Typography>
            
            <Grid2
                container
                spacing={2}
                columns={12}
                sx={{ mb: (theme) => theme.spacing(2) }}
            >
                {accounts.map((account) => (
                    <Grid2 key={account.id} size={{ xs: 12, md: 6 }}>
                        <AccountChart
                            account={account}
                            balances={balancesByAccount[account.id] ?? []}
                        />
                    </Grid2>
                ))}
            </Grid2>
        </Box>
    );
}