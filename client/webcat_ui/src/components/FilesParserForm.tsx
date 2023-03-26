import React from 'react';
import { Stack, Container, Button, Form, Row, Col } from 'react-bootstrap';
import { useFilePicker, Validator } from 'use-file-picker';
import { AppContext } from '../index';
import {Content, entity_color_mapping} from '../models/Content';

interface FilesParserStats {
    "total": number,
    "processed": number,
    "duplicate": number,
}

function FilesParserForm() {
    const [hypothesisTemplate, setHypothesisTemplate] = React.useState("This example is about {}.");
    const [labels, setLabels] = React.useState("drugs,hacking,fraud,counterfeit goods,cybercrime,cryptocurrency,delivery");
    const [path, setPath] = React.useState("");
    const [useRecursive, setUseRecursive] = React.useState(false);
    const [content, setContent] = React.useState() as [[Content], any];
    const [stats, setStats] = React.useState() as FilesParserStats | any;
    const [openFileSelector, { filesContent, loading, errors, plainFiles, clear }] = useFilePicker({
        multiple: false,
        readAs: 'DataURL',
    });
    // Read server_ip and server_port from the context
    const { server_ip, server_port, server_api } = React.useContext(AppContext);
    
    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        console.log(`Hypothesis Template: ${hypothesisTemplate} Labels: ${labels} Path: ${path} Use Recursive: ${useRecursive}`);

        // Construct the request body, which is a JSON object
        const requestBody = {
            "hypothesis_template": hypothesisTemplate,
            "labels": labels.split(','),
            "path": path,
            "recursive": useRecursive
        };

        // Send the request to the server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_files_parser`, {
            // wait forever for the response
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json(), error => console.log("Error: " + error))
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            console.log('Success:', data);
            let content = data.contents;
            let stats = data.stats;
            console.log('Success:', stats);
            // console.log('Success:', content);
            for (let c of content) {
                for (let entity of c.entities) {
                    // replace entity with <span> tag
                    c.text = c.text.replace(entity.name, `<span class='${entity_color_mapping[entity.type.name]} text-light p-1 rounded'>${entity.name}</span>`);
                }
            }
            setContent(content);
            setStats(stats);
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
                {
                    stats &&
                    <Container className='text-light mb-3 mt-3'>
                        <h3>Stats:</h3>
                        <div className='text-light mt-3'>Total content: {stats.total}</div>
                        <div className='text-light mt-3'>Processed content: {stats.processed}</div>
                        <div className='text-light mt-3'>Duplicate content: {stats.duplicate}</div>
                    </Container>
                }
                {
                    content &&
                    content.map((item) => {
                        return (
                            <Container className='text-light mb-3 mt-3'>
                                {/*an empty separator line*/}
                                <div className='border rounded text-light mb-5'></div>
                                {/* filename */}
                                <Container className='text-light mb-3'> <h3>Path to file:</h3><div className='text-light mt-3'/>{item.file}</Container>
                                <Container className='text-light mb-3'> <h3 className='mb-3'>Categories:</h3> {
                                Object.keys(item.categories).map((key) => {
                                    var score = item.categories[key];
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
                                </Container>
                                <Container className='text-light mb-5'> <h3>Text with Named Entities:</h3><div className='text-light mt-3' dangerouslySetInnerHTML={{__html: item.text}} /></Container>
                            </Container>

                            )
                        }
                    )
                }

            </Stack>
        </Container>
    );
}

export default FilesParserForm;