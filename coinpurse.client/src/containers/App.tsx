import { Routes, Route } from "react-router";
import DashboardPage from "./Pages/DashboardPage";
import SettingsPage from "./Pages/SettingsPage";
import AppLayout from "./AppLayout";
import { Box } from "@mui/material";
import CheckupPage from "./Pages/CheckupPage";

function App() {
    return (
        <Box>
            <Routes>
                <Route path="/" element={<AppLayout />}>
                    <Route index element={<CheckupPage />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Route>
            </Routes>
        </Box>
    );
}

export default App;
