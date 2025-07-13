import React, { useState } from "react";
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Select,
    MenuItem,
    FormControl,
    Stack,
    Avatar,
    Typography
} from "@mui/material";
import { Institution } from "../redux/slices/institutionsSlice";
import { TaxType } from "../redux/slices/accountsSlice";

interface CreateAccountModalProps {
    open: boolean;
    onClose: () => void;
    onSubmit: (data: any) => void;
    institutions: Institution[];
}

const CreateAccountModal: React.FC<CreateAccountModalProps> = ({ open, onClose, onSubmit, institutions}) => {
    const [institution, setInstitution] = useState("");
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [taxType, setTaxType] = useState<TaxType>(TaxType.Standard);
    const [picture, setPicture] = useState<File | null>(null);
    const [picturePreview, setPicturePreview] = useState<string | null>(null);

    const handlePictureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setPicture(e.target.files[0]);
            setPicturePreview(URL.createObjectURL(e.target.files[0]));
        }
    };

    const handleSubmit = () => {
        onSubmit({ institution, name, description, taxType, picture });
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>Create New Account</DialogTitle>
            <DialogContent>
                <Stack spacing={2}>
                    <Typography variant="subtitle2">Institution</Typography>
                    <FormControl fullWidth required>
                        <Select
                            value={institution}
                            onChange={e => setInstitution(e.target.value)}
                            displayEmpty
                        >
                            <MenuItem value="" disabled>
                                Select institution
                            </MenuItem>
                            {institutions.map((inst) => (
                                <MenuItem key={inst.id} value={inst.id}>{inst.name}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Typography variant="subtitle2">Name</Typography>
                    <TextField
                        value={name}
                        onChange={e => setName(e.target.value)}
                        required
                        fullWidth
                        placeholder="Enter account name"
                        variant="outlined"
                    />
                    <Typography variant="subtitle2">Description</Typography>
                    <TextField
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                        multiline
                        rows={2}
                        fullWidth
                        placeholder="Enter description (optional)"
                        variant="outlined"
                    />
                    <Typography variant="subtitle2">Tax Type</Typography>
                    <FormControl fullWidth required>
                        <Select
                            value={taxType}
                            onChange={e => setTaxType(e.target.value as TaxType)}
                            displayEmpty
                        >
                            <MenuItem value="" disabled>
                                Select tax type
                            </MenuItem>
                            {Object.values(TaxType).map((taxType) => (
                                <MenuItem key={taxType} value={taxType}>{taxType}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Stack direction="row" alignItems="center" spacing={2}>
                        <Stack direction="column" spacing={0.5}>
                            <Typography variant="subtitle2">Picture</Typography>
                            <Button variant="contained" component="label">
                                Upload Picture
                                <input
                                    type="file"
                                    accept="image/*"
                                    hidden
                                    onChange={handlePictureChange}
                                />
                            </Button>
                        </Stack>
                        {picturePreview && (
                            <Avatar src={picturePreview} sx={{ width: 48, height: 48 }} />
                        )}
                    </Stack>
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button onClick={handleSubmit} variant="contained" disabled={!institution || !name || !taxType}>Create</Button>
            </DialogActions>
        </Dialog>
    );
};

export default CreateAccountModal;
