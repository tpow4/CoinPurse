import { useEffect } from "react";
import {
    fetchAccounts,
    selectAllAccounts,
} from "../redux/slices/accountsSlice";
import { Grid2 } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../redux/hooks";
import {
    fetchBalances,
    selectAllBalances,
} from "../redux/slices/balancesSlice";
import AccountChart from "./AccountChart";

export default function Accounts() {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts);
    const balances = useAppSelector(selectAllBalances);

    useEffect(() => {
        dispatch(fetchAccounts());
        dispatch(fetchBalances());
    }, [dispatch]);

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
                        balances={balances.filter(
                            (b) => b.accountId === account.id
                        )}
                    />
                </Grid2>
            ))}
        </Grid2>
    );
}
