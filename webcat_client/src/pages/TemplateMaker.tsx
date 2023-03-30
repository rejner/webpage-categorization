import React from 'react';
import { Stack, Container, Button, Form } from 'react-bootstrap';
import Templater from '../components/Templater';
import TemplaterAuto from '../components/TemplaterAuto';

function TemplateMaker() {
  const [automatic, setAutomatic] = React.useState(false);

  return (
    <Container className="bg-none" >

        <Stack gap={3} >
          {/* Create a switch button, center it */}
          <Form className="d-flex flex-column align-items-center">
            <Form.Label className="text-white mt-5">Automatic Template Maker (Alpha)</Form.Label>
            <Form.Check type="switch" id="automatic-switch" onChange={() => setAutomatic(!automatic)} />
          </Form>
          {!automatic &&
            <Templater />
          }
          {automatic &&
            <TemplaterAuto />
          }
        </Stack>
    </Container>
  );
}

export default TemplateMaker;