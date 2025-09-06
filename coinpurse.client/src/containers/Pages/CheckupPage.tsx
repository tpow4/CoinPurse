import { useEffect, useState } from "react";
import { useAppSelector, useAppDispatch } from "../../redux/hooks";
import {
    selectAllAccounts,
    fetchAccounts,
} from "../../redux/slices/accountsSlice";
import {
    submitBalancesThunk,
    selectBalancesStatus,
} from "../../redux/slices/balancesSlice";
import {
    fetchPeriods,
    selectAllPeriods,
} from "../../redux/slices/periodsSlice";

import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

function CheckupPage() {
    const dispatch = useAppDispatch();
    const accounts = useAppSelector(selectAllAccounts);
    const [balances, setBalances] = useState<{ [accountId: number]: string }>(
        {}
    );
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
        const period = periods.find((p) => {
            const start = new Date(p.startDate);
            const end = new Date(p.endDate);
            return today >= start && today <= end;
        });
        if (!period) {
            setPeriodError("No fiscal period found for today.");
            return;
        }
        const payload = Object.entries(balances)
            .filter(([_, v]) => v && !isNaN(Number(v)))
            .map(([accountId, amount]) => ({
                accountId: Number(accountId),
                periodId: period.id,
                amount: Number(amount),
            }));
        if (payload.length === 0) return;
        const result = await dispatch(submitBalancesThunk(payload));
        if (submitBalancesThunk.fulfilled.match(result)) {
            setBalances({}); // clear on success
        }
    };

    return (
        <Box
            sx={{
                maxWidth: 1400,
                width: "100%",
                mx: "auto",
                px: { xs: 1, sm: 2, md: 3 },
            }}
        >
            <form autoComplete="off">
                <Stack spacing={2} sx={{ mt: 2 }}>
                    {accounts.map((account) => (
                        <Box
                            key={account.id}
                            sx={{
                                display: "flex",
                                flexDirection: { xs: "column", sm: "row" },
                                textAlign: "left",
                                alignItems: { sm: "center" },
                                gap: 2,
                                p: 2,
                                borderRadius: 2,
                                border: "1px solid #e0e0e0",
                                boxShadow: 1,
                                background: "white",
                                width: "100%",
                            }}
                        >
                            <Avatar
                                src={undefined}
                                alt={account.name}
                                sx={{ mr: { sm: 2 }, mb: { xs: 1, sm: 0 } }}
                            />
                            <Box
                                sx={{
                                    flex: 2,
                                    minWidth: 120,
                                    maxWidth: 400,
                                    flexBasis: 0,
                                    display: "flex",
                                    flexDirection: "column",
                                    alignItems: "flex-start",
                                    width: 0,
                                }}
                            >
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        width: "100%",
                                    }}
                                >
                                    {account.institutionName}
                                </Typography>
                                <Typography
                                    variant="subtitle1"
                                    sx={{
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        width: "100%",
                                    }}
                                >
                                    {account.name}
                                </Typography>
                            </Box>
                            <Box
                                sx={{
                                    flex: 2,
                                    minWidth: 120,
                                    maxWidth: 400,
                                    flexBasis: 0,
                                    display: "flex",
                                    flexDirection: "column",
                                    alignItems: "flex-start",
                                    width: 0,
                                }}
                            >
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        width: "100%",
                                    }}
                                >
                                    {"Previous Balance"}
                                </Typography>
                                <Typography
                                    variant="subtitle1"
                                    sx={{
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        width: "100%",
                                    }}
                                >
                                    {`$${
                                        account.latestBalance?.toLocaleString(
                                            "en-US",
                                            {
                                                minimumFractionDigits: 2,
                                                maximumFractionDigits: 2,
                                            }
                                        ) ?? "0.00"
                                    }`}
                                </Typography>
                            </Box>
                            <TextField
                                type="number"
                                label="Enter balance"
                                value={balances[account.id] ?? ""}
                                slotProps={{
                                    input: {
                                        startAdornment: "$",
                                        inputMode: "decimal",
                                    },
                                }}
                                sx={{ flex: 2, minWidth: 160 }}
                                onChange={(e) =>
                                    handleBalanceChange(
                                        account.id,
                                        e.target.value
                                    )
                                }
                            />
                        </Box>
                    ))}
                </Stack>
            </form>
            {periodError && (
                <Typography color="error" align="center" sx={{ mt: 2 }}>
                    {periodError}
                </Typography>
            )}
            <Stack direction="row" justifyContent="center" sx={{ mt: 4 }}>
                <Button
                    variant="contained"
                    color="secondary"
                    disabled={
                        balancesStatus === "pending" ||
                        !Object.values(balances).some(
                            (v) => v && !isNaN(Number(v))
                        )
                    }
                    onClick={handleSubmit}
                >
                    {balancesStatus === "pending"
                        ? "Submitting..."
                        : "Submit All"}
                </Button>
            </Stack>
        </Box>
    );
}

export default CheckupPage;
