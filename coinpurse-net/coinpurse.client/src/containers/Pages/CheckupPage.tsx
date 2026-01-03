import { useEffect, useState } from "react";
import { useAppSelector, useAppDispatch } from "../../redux/hooks";
import {
    selectAllAccounts,
    fetchAccounts,
} from "../../redux/slices/accountsSlice";
import {
    submitBalancesForDateThunk,
    selectBalancesStatus,
    selectBalancesError,
    clearBalancesError,
} from "../../redux/slices/balancesSlice";
import {
    fetchPeriods,
} from "../../redux/slices/periodsSlice";
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import InputAdornment from '@mui/material/InputAdornment';

function CheckupPage() {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts);
    const [balances, setBalances] = useState<{ [accountId: number]: string }>({});
    const balancesStatus = useAppSelector(selectBalancesStatus);
    const balancesError = useAppSelector(selectBalancesError);
    const [submitSuccess, setSubmitSuccess] = useState(false);

    useEffect(() => {
        dispatch(fetchAccounts());
        dispatch(fetchPeriods());
    }, [dispatch]);

    // Clear success message after 3 seconds
    useEffect(() => {
        if (submitSuccess) {
            const timer = setTimeout(() => setSubmitSuccess(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [submitSuccess]);

    const handleBalanceChange = (accountId: number, value: string) => {
        setBalances((prev) => ({ ...prev, [accountId]: value }));
        // Clear any previous errors when user starts typing
        if (balancesError) {
            dispatch(clearBalancesError());
        }
    };

    const handleSubmit = async () => {
        setSubmitSuccess(false);

        // Convert balances to the format expected by the API
        const balancesArray = Object.entries(balances)
            .filter(([value]) => value.trim() !== '' && !isNaN(parseFloat(value)))
            .map(([accountId, amount]) => ({
                accountId: parseInt(accountId),
                amount: Math.round(parseFloat(amount) * 100), // Convert to cents
            }));

        if (balancesArray.length === 0) {
            return; // Let the disabled button state handle this
        }

        try {
            await dispatch(submitBalancesForDateThunk({
                balances: balancesArray,
                targetDate: new Date()
            })).unwrap();
            
            setSubmitSuccess(true);
            setBalances({}); // Clear form on success
        } catch (error) {
            // Error is handled by Redux and displayed via balancesError
            console.error('Failed to submit balances:', error);
        }
    };

    const hasValidBalances = Object.values(balances).some(
        value => value.trim() !== '' && !isNaN(parseFloat(value)) && parseFloat(value) >= 0
    );

    return (
        <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Monthly Balance Checkup
            </Typography>
            
            <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
                Enter your current account balances. A period will be automatically created for this month if it doesn't exist.
            </Typography>

            {submitSuccess && (
                <Alert severity="success" sx={{ mb: 2 }}>
                    Balances submitted successfully!
                </Alert>
            )}

            {balancesError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {balancesError}
                </Alert>
            )}

            <Stack spacing={3}>
                {accounts.map((account) => (
                    <Box key={account.id} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
                            {account.name.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle1" fontWeight={600}>
                                {account.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {account.institutionName}
                            </Typography>
                            {!!account.latestBalance && (
                                <Typography variant="caption" color="text.secondary">
                                    Previous: ${(account.latestBalance / 100).toFixed(2)}
                                </Typography>
                            )}
                        </Box>
                        <TextField
                            type="number"
                            label="Current Balance"
                            value={balances[account.id] || ''}
                            onChange={(e) => handleBalanceChange(account.id, e.target.value)}
                            sx={{ width: 200 }}
                            slotProps={{
                                input: {
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            $
                                        </InputAdornment>
                                    ),
                                    inputProps: {
                                        min: 0,
                                        step: 0.01,
                                    }
                                },
                            }}
                            placeholder="0.00"
                            size="medium"
                        />
                    </Box>
                ))}
            </Stack>

            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
                <Button
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={balancesStatus === 'pending' || !hasValidBalances}
                    size="large"
                    sx={{ minWidth: 200, py: 1.5 }}
                >
                    {balancesStatus === 'pending' ? 'Submitting...' : 'Submit Balances'}
                </Button>
            </Box>
        </Box>
    );
}

export default CheckupPage;