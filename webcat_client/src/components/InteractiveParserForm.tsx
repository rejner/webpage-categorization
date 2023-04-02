import React from 'react';
import { Stack, Container, Button, Form, Row, Col, Card } from 'react-bootstrap';
import { AppContext } from '../index';
import { Content, entity_color_mapping } from '../models/Content';
import { ModelSpecs } from './FilesParserForm';


function InteractiveParserForm() {
    const [hypothesisTemplate, setHypothesisTemplate] = React.useState("This example is about {}.");
    const [labels, setLabels] = React.useState("drugs,hacking,fraud,counterfeit goods,cybercrime,cryptocurrency,delivery");
    const [input, setInput] = React.useState("");
    const [categories, setCategories] = React.useState();
    const [text, setText] = React.useState();
    const [availableModels, setAvailableModels] = React.useState<ModelSpecs[]>([]);
    const [classificationModel, setClassificationModel] = React.useState<ModelSpecs>();
    const [nerModel, setNerModel] = React.useState<ModelSpecs>();
    const [showModelSelection, setShowModelSelection] = React.useState(false);
    // Read server_ip and server_port from the context
    const { server_ip, server_port, server_api } = React.useContext(AppContext);
    
    React.useEffect(() => {
        // fetch available models from server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_files_parser`)
            .then(response => response.json())
            .then(data => { 
                console.log(data);
                data = JSON.parse(data);
                let models: ModelSpecs[] = data.models;
                setAvailableModels(models);
                // find default models
                let defaultClassificationModel = models.find(model => model.task === "classification" && model.default);
                let defaultNerModel = models.find(model => model.task === "ner" && model.default);
                if (defaultClassificationModel) {
                    setClassificationModel(defaultClassificationModel);
                }
                if (defaultNerModel) {
                    setNerModel(defaultNerModel);
                }
            });
    }, []);

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        // Construct the request body, which is a JSON object
        const requestBody = {
            "hypothesis_template": hypothesisTemplate,
            "labels": labels.split(','),
            "input": input,
            "models": JSON.stringify({
                "classification": classificationModel?.name,
                "ner": nerModel?.name
            })
        };
        console.log(requestBody);

        // Send the request to the server

        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_interactive`, {
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
                let content: Content = data;
                let entities: any = content.entities;
                for (let entity of entities) {
                    // replace entity with <span> tag
                    data.text = data.text.replace(entity.name, `<span class='${entity_color_mapping[entity.type]} text-light p-1 rounded'>${entity.name}</span>`);
                }
                setCategories(data.categories);
                setText(data.text);
            }

        }, error => console.log("Error: " + error)
        )
    }

    return (
        <Container className="bg-none" >
            <Stack gap={3} className="mt-4 text-light">
                <Form onSubmit={handleSubmit}>
                <Form.Switch className="mb-2" label="Show Model Selection" checked={showModelSelection} onChange={(e) => setShowModelSelection(e.target.checked)} />
                    {/* Model selection */}
                    {showModelSelection && availableModels &&
                        <Stack gap={3} direction="vertical">
                            <Form.Group controlId="formModel">
                                <Form.Label className='text-light'>Classification Model</Form.Label>
                                <Form.Select aria-label="Default select example w-25" value={classificationModel?.name} onChange={(e) => setClassificationModel(
                                    availableModels.find((model) => model.name == e.target.value)
                                )}>
                                    {
                                        availableModels.map((model, index) => {
                                            if (model.task == 'classification'){
                                                return <option key={index} value={model.name}>{model.name}</option>
                                            }
                                        
                                        })
                                    }
                                </Form.Select>
                                {
                                classificationModel && 
                                <Form.Text className="text-muted">
                                    {classificationModel.description}
                                    {classificationModel.size && <span> Size: {classificationModel.size}</span>}
                                </Form.Text>
                            }
                            </Form.Group>
          
                            <Form.Group className="mb-3" controlId="formModel">
                                <Form.Label className='text-light'>Entity Recognition Model</Form.Label>
                                <Form.Select aria-label="Default select example w-25" value={nerModel?.name} onChange={(e) => setNerModel(
                                    availableModels.find((model) => model.name == e.target.value)
                                )}>
                                    {
                                        availableModels.map((model, index) => {
                                            if (model.task == 'ner'){
                                                return <option key={index} value={model.name}>{model.name}</option>
                                            }
                                        }
                                        )
                                    }
                                </Form.Select>
                                {
                                nerModel &&
                                    <Form.Text className="text-muted">
                                        {nerModel.description}
                                        {nerModel.size && <span> Size: {nerModel.size}</span>}
                                    </Form.Text>
                                }
                            </Form.Group>
                        </Stack>
                    }
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
                    Object.keys(categories).map((key) => {
                        var score = parseFloat(categories[key]);
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
                
                {text && <Container className='text-light mb-5'> <h3>Named Entity Recognition:</h3><div className='text-light mt-3' dangerouslySetInnerHTML={{__html: text}} /></Container>}
                
                
            </Stack>
        </Container>
    );
}

export default InteractiveParserForm;