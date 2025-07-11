import { LineChart } from "@mui/x-charts/LineChart";
import { Account } from "../redux/slices/accountsSlice";
import { Balance } from "../redux/slices/balancesSlice";
import { useTheme } from "@mui/material/styles";
import { Card, CardContent, Stack, Typography } from "@mui/material";

interface AccountChartProps {
    account: Account;
    balances: Balance[];
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
    return (
        <Card variant="outlined" sx={{ width: "100%" }}>
            <CardContent>
                <div key={account.id} style={{ marginBottom: "2rem" }}>
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
                                data:
                                    balances?.map((b) =>
                                        b.periodId.toString()
                                    ) ?? [],
                                label: "Period",
                            },
                        ]}
                        series={[
                            {
                                id: "balance",
                                curve: "linear",
                                area: true,
                                data: balances?.map((b) => b.amount) ?? [],
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
                </div>
            </CardContent>
        </Card>
    );
}
