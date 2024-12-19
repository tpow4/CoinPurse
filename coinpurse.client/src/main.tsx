import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ThemeProvider } from '@mui/material/styles'
import theme from './theme/theme.tsx'
import CssBaseline from '@mui/material/CssBaseline/CssBaseline'
import { store } from './redux/store.ts'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router'

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <Provider store={store}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                    <BrowserRouter>
                        <App />
                    </BrowserRouter>
            </ThemeProvider>
        </Provider>
  </StrictMode>
);
