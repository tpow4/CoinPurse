import { useEffect } from "react";
import { fetchAccounts, selectAccountsError, selectAccountsStatus, selectAllAccounts } from "../redux/slices/accountsSlice";
import { Stack, Typography } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../redux/hooks";

export default function Accounts() {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts)
    const accountStatus = useAppSelector(selectAccountsStatus)
    const accountError = useAppSelector(selectAccountsError)

    useEffect(() => {
        dispatch(fetchAccounts());
    }, [dispatch]);

    if (accountStatus === 'pending') return <p>Loading...</p>;
    if (accountStatus === 'rejected') return <p>Error: {accountError}</p>;

    return (
        <Stack>
            {accounts.map((account) => (
                <Typography key={account.id}>{account.name}</Typography>
            ))}
        </Stack>
    );
}
