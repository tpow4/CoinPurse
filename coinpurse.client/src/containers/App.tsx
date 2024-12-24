import { Routes, Route } from "react-router";
import DashboardPage from "./DashboardPage";
import SettingsPage from "./SettingsPage";
import AppLayout from "./AppLayout";
import { Box } from "@mui/material";

function App() {
    return (
        <Box>
            <Routes>
                <Route path="/" element={<AppLayout />}>
                    <Route index element={<DashboardPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Route>
            </Routes>
        </Box>
    );
}

export default App;
