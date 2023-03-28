import React from 'react';
import { Stack, Container, Button, Form } from 'react-bootstrap';
import Templater from '../components/Templater';

function TemplateMaker() {
  return (
    <Container className="bg-none" >
        <Stack gap={3} >
            <Templater />
        </Stack>
    </Container>
  );
}

export default TemplateMaker;