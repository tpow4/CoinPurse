import React, { useState } from "react";
import { Institution } from "../redux/slices/institutionsSlice";
import { TaxType } from "../redux/slices/accountsSlice";

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
import InputLabel from '@mui/material/InputLabel';
import { CreateAccountDto } from "../services/accountService";

interface CreateAccountModalProps {
    open: boolean;
    onClose: () => void;
    onSubmit: (data: CreateAccountDto) => Promise<void>;
    institutions: Institution[];
}

const CreateAccountModal: React.FC<CreateAccountModalProps> = ({ 
    open, 
    onClose, 
    onSubmit, 
    institutions
}) => {
    const [institutionId, setInstitutionId] = useState<number | "">("");
    const [name, setName] = useState("");
    const [taxTypeId, setTaxTypeId] = useState<number | "">(""); 

    const handleSubmit = () => {
        onSubmit({ 
            institutionId: Number(institutionId), 
            name, 
            taxTypeId: Number(taxTypeId) 
        });
    };

    const handleClose = () => {
        // Reset form when closing
        setInstitutionId("");
        setName("");
        setTaxTypeId("");
        onClose();
    };

    // Convert TaxType enum to array with IDs
    const taxTypeOptions = Object.entries(TaxType)
        .filter(([key]) => !isNaN(Number(key))) // Only get numeric keys
        .map(([id, label]) => ({ id: Number(id), label: label as string }));

    return (
        <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
            <DialogTitle>Create New Account</DialogTitle>
            <DialogContent>
                <Stack spacing={3} sx={{ mt: 1 }}>
                    <FormControl fullWidth required>
                        <InputLabel>Institution</InputLabel>
                        <Select
                            value={institutionId}
                            label="Institution"
                            onChange={e => setInstitutionId(e.target.value as number)}
                        >
                            {institutions.map((institution) => (
                                <MenuItem key={institution.id} value={institution.id}>
                                    {institution.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    
                    <TextField
                        fullWidth
                        required
                        label="Account Name"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        placeholder="e.g., Checking Account, Savings, 401k"
                    />
                    
                    <FormControl fullWidth required>
                        <InputLabel>Tax Type</InputLabel>
                        <Select
                            value={taxTypeId}
                            label="Tax Type"
                            onChange={e => setTaxTypeId(e.target.value as number)}
                        >
                            {taxTypeOptions.map((option) => (
                                <MenuItem key={option.id} value={option.id}>
                                    {option.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <Button 
                    onClick={handleSubmit} 
                    variant="contained" 
                    disabled={!institutionId || !name || !taxTypeId}
                >
                    Create Account
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default CreateAccountModal;