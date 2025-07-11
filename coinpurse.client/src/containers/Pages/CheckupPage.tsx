import { Container, Stack, TextField, Typography, Avatar, Card, CardContent, CardHeader, Grid2 } from "@mui/material";
import { useEffect, useState } from 'react';
import { useAppSelector, useAppDispatch } from '../../redux/hooks';
import { selectAllAccounts, fetchAccounts } from '../../redux/slices/accountsSlice';
import { submitBalancesThunk, selectBalancesStatus } from '../../redux/slices/balancesSlice';
import { fetchPeriods, selectAllPeriods } from '../../redux/slices/periodsSlice';

function CheckupPage() {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts);
    const [balances, setBalances] = useState<{ [accountId: number]: string }>({});
    const balancesStatus = useAppSelector(selectBalancesStatus);
    const periods = useAppSelector(selectAllPeriods);
    const [periodError, setPeriodError] = useState<string | null>(null);

    useEffect(() => {
        dispatch(fetchAccounts());
        dispatch(fetchPeriods());
    }, [dispatch]);

    const handleBalanceChange = (accountId: number, value: string) => {
        setBalances((prev) => ({ ...prev, [accountId]: value }));
    };

    const handleSubmit = async () => {
        setPeriodError(null);
        const today = new Date();
        const period = periods.find(p => {
            const start = new Date(p.startDate);
            const end = new Date(p.endDate);
            return today >= start && today <= end;
        });
        if (!period) {
            setPeriodError('No fiscal period found for today.');
            return;
        }
        const payload = Object.entries(balances)
            .filter(([_, v]) => v && !isNaN(Number(v)))
            .map(([accountId, amount]) => ({
                accountId: Number(accountId),
                periodId: period.id,
                amount: Number(amount)
            }));
        if (payload.length === 0) return;
        const result = await dispatch(submitBalancesThunk(payload));
        if (submitBalancesThunk.fulfilled.match(result)) {
            setBalances({}); // clear on success
        }
    };

    return (
        <>
            <Grid2 container spacing={3} sx={{ mt: 2 }}>
                {accounts.map((account) => (
                    <Grid2 key={account.id}>
                        <Card>
                            <CardHeader
                                avatar={<Avatar src={undefined} alt={account.name} />}
                                title={account.name}
                                subheader={account.institutionName}
                            />
                            <CardContent>
                                <Stack spacing={2}>
                                    <Typography variant="body2" color="text.secondary">
                                        Previous Balance: <b>${account.latestBalance?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b>
                                    </Typography>
                                    <TextField
                                        type="number"
                                        label="Enter weekly balance"
                                        value={balances[account.id] ?? ''}
                                        InputProps={{ inputProps: { step: 0.01 } }}
                                        fullWidth
                                        onChange={(e) => handleBalanceChange(account.id, e.target.value)}
                                    />
                                </Stack>
                            </CardContent>
                        </Card>
                    </Grid2>
                ))}
            </Grid2>
            {periodError && (
                <Typography color="error" align="center" sx={{ mt: 2 }}>{periodError}</Typography>
            )}
            <Stack direction="row" justifyContent="center" sx={{ mt: 4 }}>
                <button
                    style={{ padding: '12px 32px', fontSize: '1.1rem', borderRadius: 8, background: '#1976d2', color: 'white', border: 'none', cursor: balancesStatus === 'pending' ? 'wait' : 'pointer', opacity: Object.values(balances).some(v => v && !isNaN(Number(v))) ? 1 : 0.5 }}
                    disabled={balancesStatus === 'pending' || !Object.values(balances).some(v => v && !isNaN(Number(v)))}
                    onClick={handleSubmit}
                >
                    {balancesStatus === 'pending' ? 'Submitting...' : 'Submit All'}
                </button>
            </Stack>
        </>
    );
}

export default CheckupPage;
