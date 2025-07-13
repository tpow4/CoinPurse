import "../../App.css";
import { Container, Stack, Fab } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import Accounts from "../Accounts";
import { useState } from "react";
import CreateAccountModal from "../CreateAccountModal";
import { useAppDispatch } from "../../redux/hooks";
import { createAccount } from "../../redux/slices/accountsSlice";
import { selectAllInstitutions } from "../../redux/slices/institutionsSlice";
import { useSelector } from "react-redux";
import { useEffect } from "react";
import { fetchInstitutions } from "../../redux/slices/institutionsSlice";

function DashboardPage() {
    const [open, setOpen] = useState(false);
    const dispatch = useAppDispatch();
    const institutions = useSelector(selectAllInstitutions);

    useEffect(() => {
        dispatch(fetchInstitutions());
    }, [dispatch]);

    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);
    const handleSubmit = async (data: any) => {
        const result = await dispatch(createAccount(data));
        if (createAccount.fulfilled.match(result)) {
            setOpen(false);
            alert('Account created successfully!');
        } else {
            alert('Failed to create account: ' + (result.payload || 'Unknown error'));
        }
    };

    return (
        <Stack
            spacing={2}
            sx={{
                alignItems: "center",
                mx: 3,
                pb: 5,
                mt: { xs: 8, md: 0 },
            }}
        >
            <Container maxWidth="lg" sx={{ position: 'relative' }}>
                <Accounts />
                <Fab
                    color="primary"
                    aria-label="add"
                    onClick={handleOpen}
                    sx={{
                        position: { xs: 'fixed', md: 'absolute' },
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
            </Container>
        </Stack>
    );
}

export default DashboardPage;
