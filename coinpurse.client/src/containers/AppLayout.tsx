import { Outlet } from "react-router-dom";
import TopAppBar from "./TopAppBar";
import { Box, Container } from "@mui/material";

const Layout = () => (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh", width: "100vw" }}>
        <TopAppBar />
        <Container
            component="main"
            sx={{
                flexGrow: 1,
                overflow: "auto",
                pt: 2,
                px: 2
            }}
        >
            <Outlet />
        </Container>
    </Box>
);

export default Layout;
