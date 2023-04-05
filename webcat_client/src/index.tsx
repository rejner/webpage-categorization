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

interface AppContextType {
  server_ip: string;
  setServerIp: (ip: string) => void;
  server_port: string;
  setServerPort: (port: string) => void;
  server_api: string;
  setServerApi: (api: string) => void;
}

export const AppContext = React.createContext<AppContextType>(undefined as any);

// storage for server ip, port and api
function getServerInfo() {
  const ip = localStorage.getItem('server_ip') || '127.0.0.1'
  const port = localStorage.getItem('server_port') || '5000';
  const api = localStorage.getItem('server_api') || '/api/v1';
  console.log(`Loading: serverIp: ${ip}, serverPort: ${port}, serverApi: ${api}`);
  return { ip, port, api };
}

function saveServerInfo(serverIp: string, serverPort: string, serverApi: string) {
  localStorage.setItem('server_ip', serverIp);
  localStorage.setItem('server_port', serverPort);
  localStorage.setItem('server_api', serverApi);
  console.log(`Saving: serverIp: ${serverIp}, serverPort: ${serverPort}, serverApi: ${serverApi}`);
}

export default function App() {
  const { ip, port, api } = getServerInfo();
  const [serverIp, setServerIp] = React.useState(ip);
  const [serverPort, setServerPort] = React.useState(port);
  const [serverApi, setServerApi] = React.useState(api);

  React.useEffect(() => {
    saveServerInfo(serverIp, serverPort, serverApi);
  }, [serverIp, serverPort, serverApi]);

  return (
    <div className='background-themed'>
      <AppContext.Provider value={{ server_ip: serverIp, setServerIp, server_port: serverPort, setServerPort, server_api: serverApi, setServerApi }} >
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
      </AppContext.Provider>
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
