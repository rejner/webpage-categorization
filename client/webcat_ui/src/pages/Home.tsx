import 'bootstrap/dist/css/bootstrap.min.css';
import logo from '../assets/logo.svg';
import '../styles/App.css';
import React from 'react';
import { AppContext } from '../index';
import { Col, Form, Row } from 'react-bootstrap';



function Home() {
  var { server_ip, server_port, server_api } = React.useContext(AppContext);
  const [ serverUp, setServerUp ] = React.useState(false);
  const [ serverIp, setServerIp ] = React.useState(server_ip);
  const [ serverPort, setServerPort ] = React.useState(server_port);
  const [ serverApi, setServerApi ] = React.useState(server_api);

  // ping server
  React.useEffect (() => {
    const ping_server = async () => {
      const response = await fetch(`http://${server_ip}:${server_port}${server_api}/ping`);
      const data = await response.json();
      if (data.message === 'pong') {
        setServerUp(true);
      } else {
        setServerUp(false);
      }
    }
    ping_server();
  }, [server_ip, server_port, server_api]);

  React.useEffect(() => {
  }, [serverUp]);

  function reConnect() {
    // ping server
    const ping_server = async () => {
      const response = await fetch(`http://${serverIp}:${serverPort}${serverApi}/ping`).catch((error) => {
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
        server_ip = serverIp;
        server_port = serverPort;
        server_api = serverApi;
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
        <Form onSubmit={(e) => {e.preventDefault();
                                reConnect();}
        }>
          <Form.Group controlId="formBasicEmail">
            <Form.Label>Server IP</Form.Label>
            <Form.Control type="text" placeholder="Enter server IP" value={serverIp} onChange={(e) => setServerIp(e.target.value)} />
          </Form.Group>
          <Form.Group controlId="formBasicPassword">
            <Form.Label>Server Port</Form.Label>
            <Form.Control type="text" placeholder="Enter server port" value={serverPort} onChange={(e) => setServerPort(e.target.value)} />
          </Form.Group>
          <Form.Group controlId="formBasicPassword">
            <Form.Label>Server API</Form.Label>
            <Form.Control type="text" placeholder="Enter server API" value={serverApi} onChange={(e) => setServerApi(e.target.value)} />
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
          <small className="text-muted"> {props.serverUp ? "(online)" : "(offline)"} </small>
        </div>
        
    </div>
  );
}

export default Home;