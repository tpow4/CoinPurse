import AddIcon from "@mui/icons-material/Add";
import Accounts from "../Accounts";
import { useState, useEffect } from "react";
import CreateAccountModal from "../CreateAccountModal";
import { useAppDispatch, useAppSelector } from "../../redux/hooks";
import {
    createAccount,
    selectAccountsError,
    selectAccountsStatus,
} from "../../redux/slices/accountsSlice";
import {
    selectAllInstitutions,
    fetchInstitutions,
} from "../../redux/slices/institutionsSlice";
import { useSelector } from "react-redux";
import { selectBalancesStatus } from "../../redux/slices/balancesSlice";
import { CreateAccountPayload } from "../../services/accountService";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Fab from "@mui/material/Fab";
import Box from "@mui/material/Box";
import Analytics from "@mui/icons-material/Analytics";

function DashboardPage() {
    const [open, setOpen] = useState(false);
    const dispatch = useAppDispatch();
    const institutions = useSelector(selectAllInstitutions);
    const accountStatus = useAppSelector(selectAccountsStatus);
    const accountError = useAppSelector(selectAccountsError);
    const balanceStatus = useAppSelector(selectBalancesStatus);
    const balanceError = useAppSelector(selectAccountsError);

    useEffect(() => {
        dispatch(fetchInstitutions());
    }, [dispatch]);

    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);
    const handleSubmit = async (data: CreateAccountPayload) => {
        const result = await dispatch(createAccount(data));
        if (createAccount.fulfilled.match(result)) {
            setOpen(false);
            alert("Account created successfully!");
        } else {
            alert(
                "Failed to create account: " +
                    (result.payload || "Unknown error")
            );
        }
    };

    if (accountStatus === "pending" || balanceStatus === "pending")
        return <Typography variant="h2">Loading...</Typography>;
    if (accountStatus === "rejected")
        return <Typography variant="h2">Error: {accountError}</Typography>;
    if (balanceStatus === "rejected")
        return <Typography variant="h2">Error: {balanceError}</Typography>;

    return (
        <Box sx={{ mx: "auto", p: 3 }}>
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
                    <Analytics color="primary" fontSize="large" />
                    {"Account Balance Dashboard"}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Overview of your account balances across all institutions.
                </Typography>
            </Box>
            <Stack>
                <Box sx={{ position: "relative" }}>
                    <Accounts />
                    <Fab
                        color="primary"
                        aria-label="add"
                        onClick={handleOpen}
                        sx={{
                            position: { xs: "fixed", md: "absolute" },
                            bottom: { xs: 24, md: 24 },
                            right: { xs: 24, md: 24 },
                            zIndex: 1300,
                        }}
                    >
                        <AddIcon />
                    </Fab>
                    <CreateAccountModal
                        open={open}
                        onClose={handleClose}
                        onSubmit={handleSubmit}
                        institutions={institutions}
                    />
                </Box>
            </Stack>
        </Box>
    );
}

export default DashboardPage;
