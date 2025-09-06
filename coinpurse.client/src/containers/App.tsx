import { Routes, Route } from "react-router";
import DashboardPage from "./Pages/DashboardPage";
import SettingsPage from "./Pages/SettingsPage";
import AppLayout from "./AppLayout";
import MonthlyBalanceTracker from "./Pages/MonthlyBalanceTracker";

function App() {
    return (
        <Routes>
            <Route path="/" element={<AppLayout />}>
                <Route index element={<MonthlyBalanceTracker />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/settings" element={<SettingsPage />} />
            </Route>
        </Routes>
    );
}

export default App;
