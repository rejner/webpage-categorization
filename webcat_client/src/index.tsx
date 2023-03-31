import React from 'react';
import reportWebVitals from './reportWebVitals';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Layout from "./components/Layout";
import InteractiveParser from "./pages/InteractiveParser";
import FilesParser from "./pages/FilesParser";
import TemplateMaker from "./pages/TemplateMaker";
import 'bootstrap/dist/css/bootstrap.min.css';
import TemplateManagerPage from './pages/TemplateManagerPage';
import DataViewer from './pages/DataViewerPage';

export var AppContext = React.createContext({'server_ip': '127.0.0.1',
                                               'server_port': '5000',
                                               'server_api': '/api/v1'});

export default function App() {
  return (
    <div className='background-themed'>
        <BrowserRouter>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<Home />} />
                <Route path="interactive_parser" element={<InteractiveParser />} />
                <Route path="files_parser" element={<FilesParser />} />
                <Route path="template_maker" element={<TemplateMaker />} />
                <Route path="template_manager" element={<TemplateManagerPage />} />
                <Route path="data_viewer" element={<DataViewer />} />
              </Route>
            </Routes>
      </BrowserRouter>
    </div>

  );
}

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  // TODO: Renders the App twice in development mode
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();