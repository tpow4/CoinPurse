import { Outlet } from "react-router-dom";
import TopAppBar from "./TopAppBar";
import { Box } from "@mui/material";

const Layout = () => (
    <Box sx={{ display: "flex" }}>
        <TopAppBar />
        <Box
            component="main"
            sx={{
                flexGrow: 1,
                height: "100vh",
                overflow: "auto",
                pt: 8,
                px: 3,
            }}
        >
            <Outlet />
        </Box>
    </Box>
);

export default Layout;
