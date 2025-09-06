import { Outlet } from "react-router-dom";
import TopAppBar from "./TopAppBar";
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';

const Layout = () => (
    <Box sx={{ 
        display: "flex", 
        flexDirection: "column", 
        height: "100vh"
        // Removed width: "100vw" - this causes horizontal scrollbar
    }}>
        <TopAppBar />
        <Container
            component="main"
            maxWidth="lg"
            sx={{
                flexGrow: 1,
                overflow: "auto",
                pt: 2,
                px: 2,
                pb: 2
            }}
        >
            <Outlet />
        </Container>
    </Box>
);

export default Layout;