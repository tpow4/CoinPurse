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

export default function Accounts() {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts);
    const balances = useAppSelector(selectAllBalances);

    useEffect(() => {
        dispatch(fetchAccounts());
        dispatch(fetchBalances());
        dispatch(fetchPeriods());
    }, [dispatch]);

    const balancesByAccount = useMemo(() => {
        const mapping: { [accountId: number]: typeof balances } = {};
        
        accounts.forEach(account => {
            mapping[account.id] = balances.filter(b => b.accountId === account.id);
        });
        
        return mapping;
    }, [accounts, balances]);

    return (
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
    );
}