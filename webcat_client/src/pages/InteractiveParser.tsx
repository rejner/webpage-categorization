import React from 'react';
import { Stack, Container, Button, Form } from 'react-bootstrap';
import InteractiveParserForm from '../components/InteractiveParserForm';

function InteractiveParser() {
  return (
    <Container className="bg-none" >
        <Stack gap={3} >
            <InteractiveParserForm />
        </Stack>
    </Container>
  );
}

export default InteractiveParser;