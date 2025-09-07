import { LineChart } from "@mui/x-charts/LineChart";
import { Account } from "../redux/slices/accountsSlice";
import { Balance } from "../redux/slices/balancesSlice";
import { Period, selectAllPeriods } from "../redux/slices/periodsSlice";
import { useTheme } from "@mui/material/styles";
import { useAppSelector } from "../redux/hooks";
import { useMemo } from "react";
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Box from "@mui/material/Box";

interface AccountChartProps {
    account: Account;
    balances: Balance[];
}

interface ChartDataPoint {
    period: Period;
    amount: number | null;
    label: string;
}

function AreaGradient({ color, id }: Readonly<{ color: string; id: string }>) {
    return (
        <defs>
            <linearGradient id={id} x1="50%" y1="0%" x2="50%" y2="100%">
                <stop offset="0%" stopColor={color} stopOpacity={0.5} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
        </defs>
    );
}

export default function AccountChart({
    account,
    balances,
}: Readonly<AccountChartProps>) {
    const theme = useTheme();
    const colorPalette = [theme.palette.primary.main];
    const periods = useAppSelector(selectAllPeriods);

    // Generate chart data for the last 12 periods
    const chartData = useMemo<ChartDataPoint[]>(() => {
        if (!periods.length) return [];

        // Sort periods by start date (newest first)
        const sortedPeriods = [...periods].sort((a, b) => 
            new Date(b.startDate).getTime() - new Date(a.startDate).getTime()
        );

        // Get the last 12 periods
        const last12Periods = sortedPeriods.slice(0, 12).reverse(); // Reverse to show chronologically

        // Create chart data points
        return last12Periods.map(period => {
            // Find balance for this period and account - using correct property names
            const balance = balances.find(b => b.periodId === period.id && b.accountId === account.id);
            
            // Create a readable label from the period name or date
            const startDate = new Date(period.startDate);
            const label = startDate.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short' 
            });

            return {
                period,
                amount: balance?.amount ?? null, 
                label
            };
        });
    }, [periods, balances, account.id]);

    // Prepare data for the chart
    const chartLabels = chartData.map(point => point.label);
    const chartValues = chartData.map(point => point.amount);

    // Handle empty data case
    if (chartData.length === 0) {
        return (
            <Card variant="outlined" sx={{ width: "100%" }}>
                <CardContent>
                    <Typography component="h3" variant="h5" gutterBottom>
                        {`${account.institutionName} ${account.name}`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        No period data available
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card variant="outlined" sx={{ width: "100%" }}>
            <CardContent>
                <Box key={account.id} style={{ marginBottom: "2rem" }}>
                    <Typography component="h3" variant="h5" gutterBottom>
                        {`${account.institutionName} ${account.name}`}
                    </Typography>
                    <Stack
                        direction="row"
                        sx={{
                            alignContent: { xs: "center", sm: "flex-start" },
                            alignItems: "center",
                            gap: 1,
                        }}
                    >
                        <Typography variant="h6" component="p">
                            {account.latestBalance}
                        </Typography>
                        {/* <Chip size="small" color="success" label="+35%" /> */}
                    </Stack>
                    <LineChart
                        colors={colorPalette}
                        height={250}
                        margin={{ left: 50, right: 20, top: 20, bottom: 20 }}
                        xAxis={[
                            {
                                scaleType: "point",
                                data: chartLabels,
                                label: "Period",
                            },
                        ]}
                        series={[
                            {
                                id: "balance",
                                curve: "linear",
                                area: true,
                                data: chartValues,
                                connectNulls: false, // leaves gaps for nulls
                                label: `Balance`,
                            },
                        ]}
                        grid={{ horizontal: true }}
                        slotProps={{
                            legend: {
                                hidden: true,
                            },
                        }}
                        sx={{
                            "& .MuiAreaElement-series-balance": {
                                fill: "url('#balance')",
                            },
                        }}
                    >
                        <AreaGradient
                            color={theme.palette.primary.main}
                            id="balance"
                        />
                    </LineChart>
                </Box>
            </CardContent>
        </Card>
    );
}