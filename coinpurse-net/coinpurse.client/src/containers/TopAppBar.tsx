import Typography from '@mui/material/Typography';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import { styled } from '@mui/material/styles';

const AppHeader = styled(AppBar)(({ theme }) => ({
    zIndex: theme.zIndex.drawer + 1,
}));

const TopAppBar = () => {
    return (
        <AppHeader position="static" color="primary" enableColorOnDark>
            <Toolbar>
                <Typography variant="h6" noWrap>
                    {"Coin Purse"}
                </Typography>
            </Toolbar>
        </AppHeader>
    );
};

export default TopAppBar;
