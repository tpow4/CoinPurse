import "../../App.css";
import { Container, Stack } from "@mui/material";
import Accounts from "../Accounts";

function DashboardPage() {
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
            {/* <Header /> */}
            {/* <MainGrid /> */}
            <Container maxWidth="lg">
                <Accounts />
            </Container>
        </Stack>
    );
}

export default DashboardPage;
