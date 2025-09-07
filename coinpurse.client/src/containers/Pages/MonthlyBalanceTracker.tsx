import AccountBalance from "@mui/icons-material/AccountBalance";
import CheckCircle from "@mui/icons-material/CheckCircle";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid2 from "@mui/material/Grid2";
import InputAdornment from "@mui/material/InputAdornment";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../../redux/hooks";
import {
    fetchAccounts,
    selectAllAccounts,
} from "../../redux/slices/accountsSlice";
import {
    fetchPeriods,
    selectAllPeriods,
} from "../../redux/slices/periodsSlice";
import {
    fetchBalances,
    selectAllBalances,
    submitBalancesForDateThunk,
    selectBalancesStatus,
    selectBalancesError,
    clearBalancesError,
} from "../../redux/slices/balancesSlice";

const MonthlyBalanceTracker = () => {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts);
    const periods = useAppSelector(selectAllPeriods);
    const balancesList = useAppSelector(selectAllBalances);
    const balancesStatus = useAppSelector(selectBalancesStatus);
    const balancesError = useAppSelector(selectBalancesError);
    
    const [balances, setBalances] = useState<{ [key: number]: string }>({});
    const [completedAccounts, setCompletedAccounts] = useState(new Set<number>());
    const [submitSuccess, setSubmitSuccess] = useState(false);

    // Fetch data on mount
    useEffect(() => {
        dispatch(fetchAccounts());
        dispatch(fetchPeriods());
        dispatch(fetchBalances());
    }, [dispatch]);

    // Find current period (most recent period that contains today)
    const currentPeriod = periods.find(p => {
        const today = new Date();
        const start = new Date(p.startDate);
        const end = new Date(p.endDate);
        return today >= start && today <= end;
    }) || periods.sort((a, b) => new Date(b.endDate).getTime() - new Date(a.endDate).getTime())[0];

    // Prefill balances with existing data for current period
    useEffect(() => {
        if (accounts.length > 0 && currentPeriod) {
            const initial = {} as { [key: number]: string };
            const completed = new Set<number>();

            accounts.forEach((acc) => {
                const bal = balancesList.find(
                    (b) => b.accountId === acc.id && b.periodId === currentPeriod.id
                );
                if (bal) {
                    initial[acc.id] = (bal.amount / 100).toFixed(2);
                    completed.add(acc.id);
                } else {
                    // Use latest balance as placeholder if available
                    initial[acc.id] = acc.latestBalance ? (acc.latestBalance / 100).toFixed(2) : "";
                }
            });

            setBalances(initial);
            setCompletedAccounts(completed);
        }
    }, [accounts, balancesList, currentPeriod]);

    // Clear success message after 3 seconds
    useEffect(() => {
        if (submitSuccess) {
            const timer = setTimeout(() => setSubmitSuccess(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [submitSuccess]);

    const handleBalanceChange = (accountId: number, value: string) => {
        setBalances((prev) => ({ ...prev, [accountId]: value }));
        
        // Update completed status
        if (value.trim() && !isNaN(parseFloat(value))) {
            setCompletedAccounts(prev => new Set([...prev, accountId]));
        } else {
            setCompletedAccounts(prev => {
                const newSet = new Set(prev);
                newSet.delete(accountId);
                return newSet;
            });
        }

        // Clear errors when user starts typing
        if (balancesError) {
            dispatch(clearBalancesError());
        }
    };

    const handleSubmit = async () => {
        setSubmitSuccess(false);

        // Convert balances to API format
        const balancesArray = Object.entries(balances)
            .filter(([value]) => value.trim() !== '' && !isNaN(parseFloat(value)))
            .map(([accountId, amount]) => ({
                accountId: parseInt(accountId),
                amount: Math.round(parseFloat(amount) * 100), // Convert to cents
            }));

        if (balancesArray.length === 0) return;

        try {
            await dispatch(submitBalancesForDateThunk({
                balances: balancesArray,
                targetDate: new Date()
            })).unwrap();
            
            setSubmitSuccess(true);
            // Refresh data to show updated balances
            dispatch(fetchBalances());
        } catch (error) {
            console.error('Failed to submit balances:', error);
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
        }).format(amount / 100); // Convert from cents
    };

    const progressValue = accounts.length > 0 ? (completedAccounts.size / accounts.length) * 100 : 0;

    return (
        <Box sx={{ maxWidth: 1200, mx: "auto", p: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Monthly Balance Tracker
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                    {currentPeriod 
                        ? `Current Period: ${currentPeriod.name} (${new Date(currentPeriod.startDate).toLocaleDateString()} - ${new Date(currentPeriod.endDate).toLocaleDateString()})`
                        : "Update your account balances. A new period will be created automatically."
                    }
                </Typography>

                {/* Progress */}
                <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                        <Typography variant="body2" fontWeight={500}>
                            Progress
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            {completedAccounts.size} of {accounts.length} accounts completed
                        </Typography>
                    </Box>
                    <LinearProgress
                        variant="determinate"
                        value={progressValue}
                        sx={{ height: 8, borderRadius: 4 }}
                    />
                </Box>
            </Box>

            {/* Alerts */}
            {submitSuccess && (
                <Alert severity="success" sx={{ mb: 3 }}>
                    Balances submitted successfully!
                </Alert>
            )}

            {balancesError && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {balancesError}
                </Alert>
            )}

            {/* Account Cards Grid */}
            <Grid2 container spacing={3} sx={{ mb: 4 }}>
                {accounts.map((account) => (
                    <Grid2 key={account.id} size={{ xs: 12, sm: 6, md: 4 }}>
                        <Card 
                            variant="outlined"
                            sx={{ 
                                height: "100%",
                                transition: "all 0.2s",
                                "&:hover": { boxShadow: 2 },
                                ...(completedAccounts.has(account.id) && {
                                    borderColor: "success.main",
                                    bgcolor: "success.50"
                                })
                            }}
                        >
                            <CardContent>
                                <Stack spacing={2}>
                                    {/* Account Header */}
                                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                                        <AccountBalance color="primary" />
                                        <Box sx={{ flex: 1 }}>
                                            <Typography variant="h6" component="div">
                                                {account.name}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary">
                                                {account.institutionName}
                                            </Typography>
                                        </Box>
                                        {completedAccounts.has(account.id) && (
                                            <Chip 
                                                icon={<CheckCircle />} 
                                                label="Complete" 
                                                size="small" 
                                                color="success" 
                                                variant="filled"
                                            />
                                        )}
                                    </Box>

                                    {/* Previous Balance */}
                                    {!!account.latestBalance && (
                                        <Typography variant="body2" color="text.secondary">
                                            Previous: <strong>{formatCurrency(account.latestBalance)}</strong>
                                        </Typography>
                                    )}

                                    {/* Balance Input */}
                                    <TextField
                                        fullWidth
                                        label="Current Balance"
                                        type="number"
                                        value={balances[account.id] || ""}
                                        onChange={(e) => handleBalanceChange(account.id, e.target.value)}
                                        placeholder="0.00"
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
                                        size="medium"
                                        variant="outlined"
                                    />
                                </Stack>
                            </CardContent>
                        </Card>
                    </Grid2>
                ))}
            </Grid2>

            {/* Submit Button */}
            <Box sx={{ display: "flex", justifyContent: "center" }}>
                <Button
                    variant="contained"
                    size="large"
                    onClick={handleSubmit}
                    disabled={completedAccounts.size === 0 || balancesStatus === "pending"}
                    sx={{
                        minWidth: 200,
                        py: 1.5,
                        fontWeight: 600,
                        fontSize: "1.1rem",
                    }}
                >
                    {balancesStatus === "pending" ? "Submitting..." : "Submit Balances"}
                </Button>
            </Box>
        </Box>
    );
};

export default MonthlyBalanceTracker;