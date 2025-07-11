import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './containers/App.tsx'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline/CssBaseline'
import { store } from './redux/store.ts'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router'
import theme from './Theme/Theme.tsx'

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
