import { Routes, Route } from "react-router";
import DashboardPage from "./DashboardPage";
import SettingsPage from "./SettingsPage";

function App() {
    return (
        <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/settings" element={<SettingsPage />} />
        </Routes>
    );
}

export default App;
