// Create a React component that displays our navigation bar
// There should be a top-level component that displays the navigation bar with multiple links
// The component should be called Navbar and created with functional component syntax

// Path: client/webcat_ui/src/components/Navbar.tsx

import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

export const Navigation = () => {
    return (
        <Navbar bg="dark" variant="dark" expand="lg">
            <Container>
                <Navbar.Brand href="/" className='text-light'>WebCat</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link href="/">Home</Nav.Link>
                        <Nav.Link href="/interactive_parser">Interactive Parser</Nav.Link>
                        <Nav.Link href="/files_parser">Files Parser</Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
              
    );
};

