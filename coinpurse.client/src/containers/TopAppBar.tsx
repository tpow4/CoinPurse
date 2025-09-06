import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Stack from '@mui/material/Stack';
import Avatar from '@mui/material/Avatar';
import Typography from '@mui/material/Typography';
import AppBar from '@mui/material/AppBar';
import styled from '@mui/material/styled';
import Toolbar from '@mui/material/Toolbar';

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
