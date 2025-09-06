import { Outlet } from "react-router-dom";
import TopAppBar from "./TopAppBar";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";

const Layout = () => (
    <Box
        sx={{
            display: "flex",
            flexDirection: "column",
            height: "100vh",
        }}
    >
        <TopAppBar />
        <Box
            component="main"
            sx={{
                flexGrow: 1,
                overflow: "auto",
                pt: 2,
                pb: 2,
            }}
        >
            <Container
                maxWidth="lg"
                sx={{
                    px: 2,
                }}
            >
                <Outlet />
            </Container>
        </Box>
    </Box>
);

export default Layout;
