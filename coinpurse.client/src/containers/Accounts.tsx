import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../redux/store";
import { fetchAccounts } from "../redux/slices/accountsSlice";
import { Stack, Typography } from "@mui/material";

export default function Accounts() {
    const dispatch = useDispatch<AppDispatch>();
    const { accounts, loading, error } = useSelector(
        (state: RootState) => state.accounts
    );

    useEffect(() => {
        dispatch(fetchAccounts());
    }, [dispatch]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
        <Stack>
            {accounts.map((account) => (
                <Typography key={account.id}>{account.name}</Typography>
            ))}
        </Stack>
    );
}
