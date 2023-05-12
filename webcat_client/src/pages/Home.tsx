import 'bootstrap/dist/css/bootstrap.min.css';
import logo from '../assets/logo.svg';
import '../styles/App.css';
import React from 'react';
import { AppContext } from '../index';
import { Col, Form, Row } from 'react-bootstrap';




function Home() {
  const { server_ip, setServerIp, server_port, setServerPort, server_api, setServerApi } = React.useContext(AppContext);
  const [ serverUp, setServerUp ] = React.useState(false);

  // ping server
  const ping_server = async () => {
    const response = await fetch(`http://${server_ip}:${server_port}${server_api}/ping`);
    const data = await response.json();
    if (data.message === 'pong') {
      setServerUp(true);
    } else {
      setServerUp(false);
    }
  }

  React.useEffect (() => {
    ping_server();
  }, []);

  React.useEffect(() => {
  }, [serverUp]);

  function reConnect() {
    // ping server
    const ping_server = async () => {
      const response = await fetch(`http://${server_ip}:${server_port}${server_api}/ping`).catch((error) => {
        setServerUp(false);
        return;
      });
      if (!response) {
        setServerUp(false);
        return;
      }
      const data = await response.json().catch((error) => {
        setServerUp(false);
        return;
      });
      if (data && data.message === 'pong') {
        setServerUp(true);
        // update context
      }

    }
    ping_server();
  }


  // Provide a simple form for the user to enter the server IP and port
  return (
    <div className="App">
      <header className="App-header">
      <img 
        src={'./assets/webcat_logo_smaller.png'}
        alt="logo"
        style={{width: '200px'}}
      />
      <div className='mb-5'>
        <h1>WebCat</h1>
        <h4>Webpage Categorization and Analysis Tool</h4>
      </div>
        <Form onSubmit={(e) => {e.preventDefault();
                                reConnect();}
        }>
          <Form.Group controlId="formBasicEmail">
            <Form.Label>Server IP</Form.Label>
            <Form.Control type="text" placeholder="Enter server IP" value={server_ip} onChange={(e) => setServerIp(e.target.value)} />
          </Form.Group>
          <Form.Group controlId="formBasicPassword">
            <Form.Label>Server Port</Form.Label>
            <Form.Control type="text" placeholder="Enter server port" value={server_port} onChange={(e) => setServerPort(e.target.value)} />
          </Form.Group>
          <Form.Group controlId="formBasicPassword">
            <Form.Label>Server API</Form.Label>
            <Form.Control type="text" placeholder="Enter server API" value={server_api} onChange={(e) => setServerApi(e.target.value)} />
          </Form.Group>
          {/* submit */}
          <button type="submit" className="btn btn-primary mt-3">Connect</button>

        </Form>
        {/* Display status of server (send ping to server) and display green or red cirle indicating server status */}
        <div>
          <UpDownIndicator serverUp={serverUp} />
        </div>
      </header>

      
    </div>
  );
}

function UpDownIndicator(props: any) {
  // align indicator to vertically center
  const indicatorStyle = {
    width: "20px",
    height: "20px",
    borderRadius: "50%",
    display: "inline-block",
  
    backgroundColor: props.serverUp ? "green" : "red",
  };

  return (
    <div className="mt-3">
        <div style={indicatorStyle}></div>
        <div>
          <small className="text-muted"> {props.serverUp ? "(connected)" : "(offline)"} </small>
        </div>
        
    </div>
  );
}

export default Home;