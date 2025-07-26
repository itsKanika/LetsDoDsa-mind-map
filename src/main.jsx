import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { ThemeProvider } from "./components/ThemeContext";

ReactDOM.createRoot(document.getElementById('root')).render(
   <ThemeProvider>
    <App />
  </ThemeProvider>
);

