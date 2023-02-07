import React from 'react';
import { Stack, Container, Button, Form, Row, Col } from 'react-bootstrap';
import { useFilePicker, Validator } from 'use-file-picker';
import { AppContext } from '../index';


function FilesParserForm() {
    const [hypothesisTemplate, setHypothesisTemplate] = React.useState("Talks about {}.");
    const [labels, setLabels] = React.useState("drugs,hacking,fraud,counterfeit goods,cybercrime,cryptocurrency");
    const [path, setPath] = React.useState("");
    const [useRecursive, setUseRecursive] = React.useState(false);
    const [openFileSelector, { filesContent, loading, errors, plainFiles, clear }] = useFilePicker({
        multiple: false,
        readAs: 'DataURL',
    });
    // Read server_ip and server_port from the context
    const { server_ip, server_port } = React.useContext(AppContext);
    
    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        console.log(`Hypothesis Template: ${hypothesisTemplate} Labels: ${labels} Path: ${path} Use Recursive: ${useRecursive}`);

        // Construct the request body, which is a JSON object
        const requestBody = {
            "hypothesis_template": hypothesisTemplate,
            "labels": labels.split(','),
            "path": path,
            "use_recursive": useRecursive
        };

        // Send the request to the server
        fetch(`http://${server_ip}:${server_port}/api_v1/webcat_interactive`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json(), error => console.log("Error: " + error))
        .then(data => {
            console.log('Success:', data);
        }, error => console.log("Error: " + error)
        )
    }

    return (
        <Container className="bg-none" >
            <Stack gap={3} className="mt-4">
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3" controlId="formHypothesisTemplate">
                        <Form.Label className='text-light'>Hypothesis Template</Form.Label>
                        <Form.Control type="string" placeholder="Enter hypothesis template in the form: My hypothesis {}." value={hypothesisTemplate} onChange={(e) => setHypothesisTemplate(e.target.value)}/>
                        <Form.Text className="text-muted">
                            At inference time, labels will be placed inside the {"{}"}.
                        </Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3" controlId="formLabels">
                        <Form.Label className='text-light'>Labels</Form.Label>
                        <Form.Control type="string" placeholder="Enter labels separated by ',' symbol." value={labels} onChange={(e) => setLabels(e.target.value)}/>
                    </Form.Group>

                    <Form.Group className="mb-3" controlId="formPaths">
                        <Form.Label className='text-light'>Path to Files</Form.Label>
                        <Form.Control type="string" placeholder="Enter path to files to be parsed or select files/directory."
                                      value={path} onChange={(e) => setPath(e.target.value)}/>
                    </Form.Group>


                    <Row className="mb-3">
                        <Col xs={2}>
                            <Form.Group className="mb-3" controlId="formUseRecursive">
                                <Form.Check type="checkbox" label="Use reccursive path resolution" className='text-light' checked={useRecursive} onChange={(e) => setUseRecursive(e.target.checked)}/>
                            </Form.Group>
                        </Col>

                        {/* <Col>
                            <Button variant="primary" onClick={openFileSelector}>
                                Select Files/Directory
                            </Button>
                        </Col> */}
                    </Row>

                    <Button variant="primary" type="submit">
                        Parse
                    </Button>
                </Form>
                <div className="border rounded text-light">First item</div>
                <div className="border rounded text-light">Second item</div>
                <div className="border rounded text-light">Third item</div>
            </Stack>
        </Container>
    );
}

export default FilesParserForm;