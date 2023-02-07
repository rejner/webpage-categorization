import React from 'react';
import { Stack, Container, Button, Form, Row, Col, Card } from 'react-bootstrap';
import { useFilePicker, Validator } from 'use-file-picker';
import { AppContext } from '../index';


function InteractiveParserForm() {
    const [hypothesisTemplate, setHypothesisTemplate] = React.useState("Talks about {}.");
    const [labels, setLabels] = React.useState("drugs, hacking, fraud, counterfeit goods, cybercrime, cryptocurrency");
    const [input, setInput] = React.useState("");
    const [categories, setCategories] = React.useState();
    const [text, setText] = React.useState();
    const [openFileSelector, { filesContent, loading, errors, plainFiles, clear }] = useFilePicker({
        multiple: false,
        readAs: 'DataURL',
    });
    // Read server_ip and server_port from the context
    const { server_ip, server_port } = React.useContext(AppContext);
    
    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        console.log(`Hypothesis Template: ${hypothesisTemplate} Labels: ${labels}`);

        // Construct the request body, which is a JSON object
        const requestBody = {
            "hypothesis_template": hypothesisTemplate,
            "labels": labels.split(','),
            "input": input,
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
            if (data.error) {
                alert(data.error)
            } else {
                setCategories(data.categories);
                setText(data.text);
            }

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

                    <Form.Group className="mb-3" controlId="formInput">
                        <Form.Label className='text-light'>Input</Form.Label>
                        <Form.Control  as="textarea" rows={3} placeholder="Enter text to be parsed." value={input} onChange={(e) => setInput(e.target.value)} />
                    </Form.Group>

                    <Button variant="primary" type="submit">
                        Parse
                    </Button>
                </Form>
                {/* categories is an array of 1 element with an object where keys are categories and values are scores */}
                {categories && text && 
                <Container className='text-light'> <h3 className='mb-3'>Categories:</h3> {
                    Object.keys(categories[0]).map((key) => {
                        var score = parseFloat(categories[0][key]);
                        var color = 'bg-danger';
                        if (score > 0.5) {
                            color = 'bg-success';
                        }
                        else if (score > 0.25) {
                            color = 'bg-warning';
                        }
                        // predefine className and add color to it
                        var className = 'text-light m-1 p-1 rounded w-50 ' + color;
                        return (
                        // set background color based on score
                        <Row className={className} style={{backgroundColor: color}}> 
                            <Col>{key}</Col>
                            <Col>{score.toFixed(2)}</Col>
                        </Row>
                        );
                    }
                    
                )}
                </Container>}
                {/* text contains tags which should be added into DOM */}
                
                {text && <Container className='text-light mb-5'> <h3>Named Entity Recognition:</h3><div className='text-light mt-3' dangerouslySetInnerHTML={{__html: text[0]}} /></Container>}
                
                
            </Stack>
        </Container>
    );
}

export default InteractiveParserForm;