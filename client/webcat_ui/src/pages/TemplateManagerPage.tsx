import React from 'react';
import { Stack, Container, Button, Form } from 'react-bootstrap';
import TemplateManager from '../components/TemplateManager';

function TemplateManagerPage() {
  return (
    <Container className="bg-none" >
        <Stack gap={3} >
            <TemplateManager />
        </Stack>
    </Container>
  );
}

export default TemplateManagerPage;