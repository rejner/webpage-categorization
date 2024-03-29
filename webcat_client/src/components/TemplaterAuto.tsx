import React, { useState, useEffect } from 'react';
import { Container, Button, Form, Row, Col, Spinner, Stack } from 'react-bootstrap';
import { useFilePicker } from 'use-file-picker';
import { AppContext } from '..';
import { Template } from '../models/Template';
import { Element } from '../models/Element';


interface ModelSpecs {
    name: string;
    requiresKey: boolean;
    description?: string;
}

interface TemplateProposal {
    perfect_match: boolean,
    elements: Element[],
    contents: {
        'post-author': string[],
        'post-message': string[],
        'post-title': string[],
    }

}

interface TemplateEngineResponse {
    'template': TemplateProposal,
    'error': string,
    'response': string,
    'prompt': string,
    'total_tokens': string,
}

function TemplaterAuto() {
    const [availableModels, setAvailableModels] = useState<ModelSpecs[]>([]);
    const [selectedModel, setSelectedModel] = useState<ModelSpecs>();
    const { server_ip, server_port, server_api } = React.useContext(AppContext);
    const [templateProposal, setTemplateProposal] = useState<TemplateProposal>();
    const [filePath, selectFilePah] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [isParsing, setIsParsing] = useState(false);
    const [modelResponse, setModelResponse] = useState<string>();
    const [modelPrompt, setModelPrompt] = useState<string>();
    const [totalTokens, setTotalTokens] = useState<string>();


    useEffect(() => {
        // fetch available models from server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates/engine`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                data = JSON.parse(data);
                setAvailableModels(data);
            });
    }, []);

    function parseFile() {
        if (!selectedModel) {
            alert('Please select a model');
            return;
        }
        setIsParsing(true);
        // send file to server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates/engine`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: selectedModel.name,
                file_path: filePath,
                key: apiKey,
            }),
        })
        .then(response => response.json(), error => console.log("Error: " + error))
        .then(data => {
            if (data.error) {
                setIsParsing(false);
                if (data.response) {
                    setModelResponse(data.response);
                }
                if (data.prompt) {
                    setModelPrompt(data.prompt);
                }
                if (data.total_tokens) {
                    setTotalTokens(data.total_tokens);
                }
                alert(data.error);
                return;
            }
            data = JSON.parse(data);
            let response: TemplateEngineResponse = data;
            let proposal: TemplateProposal = response.template;
            console.log(proposal);
            setTemplateProposal(proposal);  
            setModelResponse(response.response);
            setModelPrompt(response.prompt);
            setTotalTokens(response.total_tokens);
            setIsParsing(false);
        });
    }

    function saveTemplate() {
        if (!templateProposal) {
            alert('Please parse a file first');
            return;
        }
        let template: Template = {
            id: 0,
            creation_date: new Date().toISOString(),
            origin_file: filePath,
            elements: templateProposal.elements,
        };

        // send file to server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates/templates`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template: template,
                version: 2,
            }),
        })
        .then(response => response.json(), error => {
            console.log("Error: " + error);
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            data = JSON.parse(data);
            console.log(data);
            alert('Template saved');
        });
    }


        
    useEffect(() => {
        console.log('templateProposal changed');
        console.log(templateProposal);
    }, [templateProposal]);



    // A component where user can select Model for inference, file to infer on, and a button to start inference
      return (
        <>
        <Container className="bg-none text-light justify-content-center d-flex">
            {/* Model selector */}
            <Form className="w-50">
                <Form.Group controlId="formAutoParsing">
                    <Form.Label>Template Engine</Form.Label>
                        <Form.Control className="w-100" as="select" onChange={(e) => setSelectedModel(availableModels.filter(model => model.name === e.target.value)[0])} defaultValue={"Select Model"}>
                            {availableModels.map(model => <option key={model.name}>{model.name}</option>)}
                            <option key="default" disabled selected>Select a model</option>
                        </Form.Control>
                        <div className="mt-2">
                            {selectedModel && selectedModel.description &&
                            <Form.Text className="text-muted">
                                {selectedModel.description}
                            </Form.Text>
                            }
                        </div>
                 
                    { selectedModel && selectedModel.requiresKey &&
                    <>
                        <Form.Label className="mt-2"> API Key</Form.Label>
                        <Form.Control type="text" placeholder="Enter API Key" onChange={(e) => setApiKey(e.target.value)} />
                    </>
                    }
                    <Form.Label className="mt-2">File Path</Form.Label>
                    <Form.Control type="text" placeholder="Enter File Path" onChange={(e) => selectFilePah(e.target.value)} />
                </Form.Group>
 
                <Stack direction="horizontal" gap={3}>

                    <Button className="mt-4" variant="primary" onClick={parseFile} disabled={isParsing}>
                        {isParsing ? <Spinner animation="border" size="sm" /> : 'Parse File'}
                    </Button>
                    
                    {templateProposal &&
                        <Button className="mt-4" variant="success" onClick={() => saveTemplate()}>Save Template</Button>
                    }
                    {templateProposal &&
                        <Button className="mt-4" variant="danger" onClick={() => setTemplateProposal(undefined)}>Clear</Button>
                    }
                </Stack>

            </Form>

        </Container>
        <Container className="bg-none text-light justify-content-center d-flex align-items-center mt-5">
            {/* Template proposal */}
            {templateProposal && templateProposal.elements && 
            <div className="w-75">
                <h3>Template Proposal</h3>
                {/* display TemplateElements from Template */}
                <div > {/* Arrow right symbol: &#8594; */}
                    {
                        templateProposal.elements.map((element, index) => {
                            return <h6 key={index}>{index + 1}: {element.type.tag}:  depth: ({element.depth}), {element.tag} {"-->"} {element.parent_tag} {"-->"} {element.grandparent_tag} </h6>
                        }
                            )
                    }


                </div>
                <div>
                    {/* Print counts of each conten */}
                    <h6>{'# Of Titles:'}: {templateProposal.contents['post-title'].length}</h6>
                    <h6>{'# Of Authors:'}: {templateProposal.contents['post-author'].length}</h6>
                    <h6>{'# Of Messages'}: {templateProposal.contents['post-message'].length}</h6>
                    <h6> Perfect Match: {templateProposal.perfect_match ? 'True' : 'False'}</h6>
                </div>
            </div>
            }
        </Container>
        <Container className="bg-none text-light justify-content-center d-flex align-items-center">
            {/* Template contents */}
            {templateProposal && templateProposal.contents &&
            
            <div className="w-75">
                <h3>Template Contents</h3>
                <div className="w-100">
                    <h4>{'post-title'}</h4>
                    {
                        templateProposal.contents['post-title'].map((title, index) => {
                            return <p key={index}> <b>#{index}:</b> {title}</p>
                        })
                    }
                    <h4>{'post-author'}</h4>
                    {   
                        templateProposal.contents['post-author'].map((author, index) => {
                            // index should have a bold tag around it
                            return <p key={index}> <b>#{index}:</b> {author}</p>

                            
                        })
                    }
                    <h4>{'post-message'}</h4>
                    {
                        templateProposal.contents['post-message'].map((message, index) => {
                            return <p key={index}><b>#{index}:</b> {message}</p>
                        })
                    }
                </div>
            </div>
            }
        </Container>
        
        <Stack direction="vertical" gap={3} className="mb-5 text-light">
            { totalTokens &&
            <>
                <h3>Total Tokens: {totalTokens}</h3>
            </>
            }
            { modelPrompt && 
            <>  
                <h3>Model Prompt</h3>
                <p>{modelPrompt}</p>
            </>
            }
            { modelResponse &&
            <>
                <h3>Model Response</h3>
                <p>{modelResponse}</p>
            </>
            }
        </Stack>
        </>    
      );

}

export default TemplaterAuto;
