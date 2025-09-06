import AccountBalance from "@mui/icons-material/AccountBalance";
import CheckCircle from "@mui/icons-material/CheckCircle";
import ExpandMore from "@mui/icons-material/ExpandMore";
import TrendingUp from "@mui/icons-material/TrendingUp";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
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
    submitBalancesThunk,
} from "../../redux/slices/balancesSlice";

const MonthlyBalanceTracker = () => {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts);
    const periods = useAppSelector(selectAllPeriods);
    const balancesList = useAppSelector(selectAllBalances);
    const [balances, setBalances] = useState<{ [key: number]: string }>({});
    const [submitStatus, setSubmitStatus] = useState("idle"); // idle, pending, success, error
    const [completedAccounts, setCompletedAccounts] = useState(
        new Set<number>()
    );

    // Fetch accounts, periods, and balances on mount
    useEffect(() => {
        dispatch(fetchAccounts());
        dispatch(fetchPeriods());
        dispatch(fetchBalances());
    }, [dispatch]);

    // Select the current period (latest by endDate)
    const currentPeriod =
        periods.length > 0
            ? periods.reduce(
                  (latest, p) =>
                      new Date(p.endDate) > new Date(latest.endDate)
                          ? p
                          : latest,
                  periods[0]
              )
            : null;

    // Optionally, prefill balances with latestBalance for each account
    useEffect(() => {
        if (accounts.length > 0 && currentPeriod) {
            const initial = {} as { [key: number]: string };
            accounts.forEach((acc) => {
                // Find balance for this account and period
                const bal = balancesList.find(
                    (b) =>
                        b.accountId === acc.id &&
                        b.periodId === currentPeriod.id
                );
                initial[acc.id] = bal ? bal.amount.toString() : "";
            });
            setBalances(initial);
        }
    }, [accounts, balancesList, currentPeriod]);

    const handleBalanceChange = (accountId: number, value: string) => {
        setBalances((prev) => ({ ...prev, [accountId]: value }));
        // Mark as completed if value is entered
        if (value && value.trim() !== "") {
            setCompletedAccounts((prev) => new Set([...prev, accountId]));
        } else {
            setCompletedAccounts((prev) => {
                const newSet = new Set(prev);
                newSet.delete(accountId);
                return newSet;
            });
        }
    };

    const handleSubmit = async () => {
        setSubmitStatus("pending");
        try {
            const balanceData = Object.entries(balances)
                .filter(([value]) => value && value.trim() !== "")
                .map(([accountId, amount]) => ({
                    accountId: parseInt(accountId),
                    periodId: currentPeriod?.id ?? 0,
                    amount: parseInt(amount),
                }));
            await dispatch(submitBalancesThunk(balanceData)).unwrap();
            setSubmitStatus("success");
            setTimeout(() => setSubmitStatus("idle"), 3000);
        } catch (error) {
            setSubmitStatus("error");
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
        }).format(amount);
    };

    const progress =
        accounts.length > 0
            ? (completedAccounts.size / accounts.length) * 100
            : 0;

    if (!currentPeriod) {
        return <Typography>Loading period data...</Typography>;
    }

    return (
        <Box sx={{ maxWidth: 900, mx: "auto", p: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography
                    variant="h4"
                    gutterBottom
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        fontWeight: 600,
                    }}
                >
                    <AccountBalance color="primary" fontSize="large" />
                    Monthly Balance Entry
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Record account balances for {currentPeriod.name}
                </Typography>
            </Box>

            {/* Progress Indicator */}
            <Card
                sx={{
                    mb: 3,
                    bgcolor: "primary.50",
                    border: 1,
                    borderColor: "primary.200",
                }}
            >
                <CardContent>
                    <Stack
                        direction="row"
                        alignItems="center"
                        justifyContent="space-between"
                        sx={{ mb: 2 }}
                    >
                        <Typography variant="h6" fontWeight={600}>
                            Progress
                        </Typography>
                        <Chip
                            label={`${completedAccounts.size}/${accounts.length} completed`}
                            color={
                                completedAccounts.size === accounts.length &&
                                accounts.length > 0
                                    ? "success"
                                    : "default"
                            }
                            variant={
                                completedAccounts.size === accounts.length &&
                                accounts.length > 0
                                    ? "filled"
                                    : "outlined"
                            }
                        />
                    </Stack>
                    <LinearProgress
                        variant="determinate"
                        value={progress}
                        sx={{
                            height: 8,
                            borderRadius: 4,
                            bgcolor: "grey.200",
                            "& .MuiLinearProgress-bar": {
                                borderRadius: 4,
                            },
                        }}
                    />
                </CardContent>
            </Card>

            <Grid2 container spacing={3} sx={{ mb: 4 }}>
                {accounts.map((account) => (
                    <Grid2 key={account.id} size={{ xs: 12, sm: 6 }}>
                        <Card
                            elevation={
                                completedAccounts.has(account.id) ? 4 : 1
                            }
                            sx={{
                                height: "100%",
                                border: 2,
                                borderColor: completedAccounts.has(account.id)
                                    ? "success.main"
                                    : "grey.200",
                                transition: "all 0.2s ease-in-out",
                                "&:hover": {
                                    borderColor: completedAccounts.has(
                                        account.id
                                    )
                                        ? "success.main"
                                        : "grey.400",
                                    elevation: 3,
                                },
                            }}
                        >
                            <CardContent>
                                <Stack spacing={2.5}>
                                    <Box>
                                        <Typography
                                            variant="h6"
                                            gutterBottom
                                            fontWeight={600}
                                        >
                                            {account.name}
                                        </Typography>
                                        <Typography
                                            variant="body2"
                                            color="text.secondary"
                                        >
                                            {account.institutionName}
                                        </Typography>
                                    </Box>

                                    <Box>
                                        <Typography
                                            variant="body2"
                                            color="text.secondary"
                                            gutterBottom
                                            sx={{ mb: 1.5 }}
                                        >
                                            Previous Balance:{" "}
                                            <strong>
                                                {formatCurrency(
                                                    account.latestBalance
                                                )}
                                            </strong>
                                        </Typography>
                                        <TextField
                                            fullWidth
                                            label="Current Balance"
                                            type="number"
                                            value={balances[account.id] || ""}
                                            onChange={(e) =>
                                                handleBalanceChange(
                                                    account.id,
                                                    e.target.value
                                                )
                                            }
                                            placeholder="0.00"
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        $
                                                    </InputAdornment>
                                                ),
                                            }}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>

                                    {completedAccounts.has(account.id) && (
                                        <Box
                                            sx={{
                                                display: "flex",
                                                alignItems: "center",
                                                color: "success.main",
                                            }}
                                        >
                                            <CheckCircle
                                                fontSize="small"
                                                sx={{ mr: 1 }}
                                            />
                                            <Typography
                                                variant="body2"
                                                fontWeight={500}
                                            >
                                                Complete
                                            </Typography>
                                        </Box>
                                    )}
                                </Stack>
                            </CardContent>
                        </Card>
                    </Grid2>
                ))}
            </Grid2>

            {/* Historical View Accordion */}
            <Accordion sx={{ mb: 4, border: 1, borderColor: "grey.300" }}>
                <AccordionSummary
                    expandIcon={<ExpandMore />}
                    sx={{
                        "&:hover": {
                            bgcolor: "grey.50",
                        },
                    }}
                >
                    <Typography
                        variant="h6"
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1,
                            fontWeight: 600,
                        }}
                    >
                        <TrendingUp color="primary" />
                        View Historical Balances
                    </Typography>
                </AccordionSummary>
                <AccordionDetails>
                    <Typography variant="body1" color="text.secondary">
                        Historical balance data and trends would be displayed
                        here. This could include charts showing balance changes
                        over time, year-over-year comparisons, and growth
                        analytics.
                    </Typography>
                </AccordionDetails>
            </Accordion>

            {/* Submit Button */}
            <Box sx={{ display: "flex", justifyContent: "center" }}>
                <Button
                    variant="contained"
                    size="large"
                    onClick={handleSubmit}
                    disabled={
                        completedAccounts.size === 0 ||
                        submitStatus === "pending"
                    }
                    sx={{
                        minWidth: 200,
                        py: 1.5,
                        fontWeight: 600,
                        fontSize: "1.1rem",
                    }}
                >
                    {submitStatus === "pending"
                        ? "Submitting..."
                        : "Submit Balances"}
                </Button>
            </Box>
        </Box>
    );
};

export default MonthlyBalanceTracker;
