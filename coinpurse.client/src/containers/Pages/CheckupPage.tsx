import { Container, Grid2, Stack, TextField, Typography } from "@mui/material";

function CheckupPage() {
    return (
        <Grid2
            container
            spacing={{ xs: 2, md: 3 }}
            columns={{ xs: 4, sm: 8, md: 12 }}
        >
            {Array.from(Array(6)).map((_, index) => (
                <Grid2 key={index} size={6}>
                    <Container
                        sx={{
                            height: 200,
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            backgroundColor: "#f0f0f0",
                            borderRadius: 2,
                        }}
                    >
                        <Stack direction="row" spacing={2}>
                            <Stack spacing={2} alignItems={"start"}>
                                <Typography>{"Account Name"}</Typography>
                                <TextField
                                    type="number"
                                    label="Test it"
                                    value={0}
                                    onChange={(event) => {
                                        // TODO: Handle the change event
                                    }}
                                    slotProps={{
                                        htmlInput: {
                                            step: 1,
                                        },
                                    }}
                                    onWheel={(event) => {
                                        // `event.currentTarget` is a callable type but is targetting the MUI element
                                        // whereas `event.target` targets the input element but does not have the callable type, so casting
                                        (
                                            event.target as HTMLInputElement
                                        ).blur();
                                    }}
                                />
                            </Stack>
                            <Stack spacing={2} alignItems={"start"}>
                                <Typography>{"Latest balance"}</Typography>
                                <Typography>{"$0.00"}</Typography>
                            </Stack>
                        </Stack>
                    </Container>
                </Grid2>
            ))}
        </Grid2>
    );
}

export default CheckupPage;
