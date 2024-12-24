import { AppBar, styled, Toolbar, Typography } from "@mui/material";

const AppHeader = styled(AppBar)(({ theme }) => ({
    zIndex: theme.zIndex.drawer + 1,
}));

const TopAppBar = () => {
    return (
        <AppHeader position="fixed">
            <Toolbar>
                <Typography variant="h6" noWrap>
                    My Application
                </Typography>
            </Toolbar>
        </AppHeader>
    );
};

export default TopAppBar;
