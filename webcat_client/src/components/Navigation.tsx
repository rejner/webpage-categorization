import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

export const Navigation = () => {
    return (
        <Navbar bg="dark" variant="dark" expand="lg">
            <Container>
                {/* logo image */}
                <Navbar.Brand href="/">
                    <img
                        src="./assets/webcat_logo_smaller.png"
                        width="30"
                        height="30"
                        className="d-inline-block align-top"
                        alt="WebCat logo"
                    />
                </Navbar.Brand>
                <Navbar.Brand href="/" className='text-light'>WebCat</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link href="/">Home</Nav.Link>
                        <Nav.Link href="/interactive_parser">Interactive Parser</Nav.Link>
                        <Nav.Link href="/files_parser">Files Parser</Nav.Link>
                        <Nav.Link href="/template_maker">Template Maker</Nav.Link>
                        <Nav.Link href="/template_manager">Template Manager</Nav.Link>
                        <Nav.Link href="/data_viewer">Data Viewer</Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
              
    );
};

