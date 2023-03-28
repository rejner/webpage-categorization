import React from 'react';
import { Stack, Container, Button, Form } from 'react-bootstrap';
import FilesParserForm from '../components/FilesParserForm';

function InteractiveParser() {
  return (
    <Container className="bg-none" >
        <Stack gap={3} >
            <FilesParserForm />
        </Stack>
    </Container>
  );
}

export default InteractiveParser;