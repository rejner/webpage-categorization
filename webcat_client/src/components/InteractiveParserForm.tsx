import React from 'react';
import { Stack, Container, Button, Form, Row, Col, Card, Spinner } from 'react-bootstrap';
import { AppContext } from '../index';
import { InteractiveContent, entity_color_mapping } from '../models/Content';
import { ModelSpecs, ClassificationModelSpecs, NerModelSpecs } from './FilesParserForm';

export const hypothesis_presets = [
    "The text examines the topic of {} in depth.",
    "The topic of this text is {}.",
    "The text provides information about {}.",
    "The text discusses {}.",
    "The text contains information relevant to {}.",
    "The text provides insights into {}.",
    "The text sheds light on {}.",
    "The text explores {} in detail.",
    "The text provides a comprehensive analysis of {}.",
    "The text covers the topic of {} extensively.",
    "The text delves deeply into the topic of {}.",
    "The example is about {}."
]

export const label_presets = [
    "drugs,hacking,fraud,cryptocurrency,delivery,weapons,porn,childporn,software,investing,politics",
    "crypto mining, crypto trading, bitcoin",
]

function InteractiveParserForm() {
    const [hypothesisTemplate, setHypothesisTemplate] = React.useState("This example is about {}.");
    const [labels, setLabels] = React.useState(label_presets[0]);
    const [input, setInput] = React.useState("");
    const [categories, setCategories] = React.useState();
    const [text, setText] = React.useState();
    const [availableModels, setAvailableModels] = React.useState<ModelSpecs>();
    const [classificationModel, setClassificationModel] = React.useState<ClassificationModelSpecs>();
    const [nerModel, setNerModel] = React.useState<NerModelSpecs>();
    const [showModelSelection, setShowModelSelection] = React.useState(false);
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [showLabelPresets, setShowLabelPresets] = React.useState(false);
    const [showHypothesisPresets, setShowHypothesisPresets] = React.useState(false);
    // Read server_ip and server_port from the context
    const { server_ip, server_port, server_api } = React.useContext(AppContext);
    
    React.useEffect(() => {
        // fetch available models from server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_files_parser`)
            .then(response => response.json())
            .then(data => { 
                console.log(data);
                data = JSON.parse(data);
                let models: ModelSpecs = data.models;
                setAvailableModels(models);
                // find default models
                let defaultClassificationModel = models.classification.find(model => model.default);
                let defaultNerModel = models.ner.find(model => model.default);
                if (defaultClassificationModel) {
                    setClassificationModel(defaultClassificationModel);
                    setHypothesisTemplate(defaultClassificationModel.default_hypothesis);
                }
                if (defaultNerModel) {
                    setNerModel(defaultNerModel);
                }
            });
    }, []);

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsSubmitting(true);

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
                let content: InteractiveContent = data;
                let entities: any = content.entities;
                for (let entity of entities) {
                    // replace entity with <span> tag
                    data.text = data.text.replace(entity.name, `<span class='${entity_color_mapping[entity.type]} text-light p-1 rounded'>${entity.name}</span>`);
                }
                setCategories(data.categories);
                setText(data.text);
            }

        }, error => console.log("Error: " + error)
        ).finally(() => setIsSubmitting(false));
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
                                <Form.Select aria-label="Default select example w-25" value={classificationModel?.name} onChange={(e) => 
                                {
                                    let model: ClassificationModelSpecs = availableModels.classification.find((model) => model.name == e.target.value)!;
                                    setClassificationModel(model);
                                    setHypothesisTemplate(model.default_hypothesis);
                                }}>
                                    {
                                        availableModels.classification.map((model, index) => {
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
                                    availableModels.ner.find((model) => model.name == e.target.value)
                                )}>
                                    {
                                        availableModels.ner.map((model, index) => {
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
                        <Form.Switch className="mb-2" label="Show pre-defined hypothesis templates" checked={showHypothesisPresets} onChange={(e) => setShowHypothesisPresets(e.target.checked)} />
                        {/* Selector of pre-defined hypothesis templates */}
                        {
                            showHypothesisPresets &&
                            <Form.Select aria-label="Default select example" className='w-50 mb-2' onChange={(e) => setHypothesisTemplate(e.target.value)}>
                            {
                                hypothesis_presets.map((hypothesis, index) => {
                                    return <option key={index} value={hypothesis}>{hypothesis}</option>
                                })
                            }
                            </Form.Select>
                        }
             
                        <Form.Control type="string" placeholder="Enter hypothesis template in the form: My hypothesis {}." value={hypothesisTemplate} onChange={(e) => setHypothesisTemplate(e.target.value)}/>
                        <Form.Text className="text-muted">
                            At inference time, labels will be placed inside the {"{}"}.
                        </Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3" controlId="formLabels">
                        <Form.Label className='text-light'>Labels</Form.Label>
                        <Form.Switch className="mb-2" label="Show pre-defined labels" checked={showLabelPresets} onChange={(e) => setShowLabelPresets(e.target.checked)} />
                        {
                            showLabelPresets &&
                            <Form.Select aria-label="Default select example" className='w-50 mb-2' onChange={(e) => setLabels(e.target.value)}>
                            {
                                label_presets.map((label, index) => {
                                    return <option key={index} value={label}>{label}</option>
                                })
                            }
                            </Form.Select>
                        }
             
                        <Form.Control type="string" placeholder="Enter labels separated by ',' symbol." value={labels} onChange={(e) => setLabels(e.target.value)}/>
                    </Form.Group>

                    <Form.Group className="mb-3" controlId="formInput">
                        <Form.Label className='text-light'>Input</Form.Label>
                        <Form.Control  as="textarea" rows={3} placeholder="Enter text to be parsed." value={input} onChange={(e) => setInput(e.target.value)} />
                    </Form.Group>

                    <Button variant="primary" type="submit" className='w-25' disabled={isSubmitting}>
                        {isSubmitting && <Spinner animation="border" size="sm" />}
                        {!isSubmitting && <span>Submit</span>}
                    </Button>
                </Form>
                {/* categories is an array of 1 element with an object where keys are categories and values are scores */}
                {categories && text && 
                <Container className='text-light'> <h3 className='mb-3'>Categories:</h3> {
                    Object.keys(categories).map((key) => {
                        var score = parseFloat(categories[key]);
                        var color = 'bg-danger';
                        if (score > 0.8) {
                            color = 'bg-success';
                        }
                        else if (score > 0.5) {
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