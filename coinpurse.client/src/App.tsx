import { LineChart } from "@mui/x-charts/LineChart";
import "./App.css";
import { Box, Container, Grid2, Stack, Typography } from "@mui/material";
import FinancialChart from "./FinancialChart";

function App() {
  return (
    <Box sx={{ display: "flex" }}>
      {/* <SideMenu /> */}
      {/* <AppNavbar /> */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: "100vh",
          overflow: "auto",
          pt: 8,
          px: 3,
        }}
      >
        <Stack
          spacing={2}
          sx={{
            alignItems: "center",
            mx: 3,
            pb: 5,
            mt: { xs: 8, md: 0 },
          }}
        >
          {/* <Header /> */}
          {/* <MainGrid /> */}
          <Container maxWidth="lg">
            <Grid2
              container
              spacing={2}
              columns={12}
              sx={{ mb: (theme) => theme.spacing(2) }}
            >
              <Grid2 size={{ xs: 12, md: 6 }}>
                <FinancialChart/>
              </Grid2>
              <Grid2 size={{ xs: 12, md: 6 }}>
                <Typography>Test Graph</Typography>
                <LineChart
                  xAxis={[{ data: [1, 2, 3, 5, 8, 10] }]}
                  series={[
                    {
                      data: [2, 5.5, 2, 8.5, 1.5, 5],
                    },
                  ]}
                  width={500}
                  height={300}
                />
              </Grid2>
            </Grid2>
          </Container>
        </Stack>
      </Box>
    </Box>
  );
}

export default App;
