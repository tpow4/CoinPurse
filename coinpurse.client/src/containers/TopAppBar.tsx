import { AppBar, styled, Toolbar, Typography } from "@mui/material";

const AppHeader = styled(AppBar)(({ theme }) => ({
    zIndex: theme.zIndex.drawer + 1,
}));

const TopAppBar = () => {
    return (
        <AppHeader position="fixed">
            <Toolbar>
                <Typography variant="h6" noWrap>
                    {"Coin Purse"}
                </Typography>
            </Toolbar>
        </AppHeader>
    );
};

export default TopAppBar;
