import React from 'react';
import { Stack, Container, Button, Form, Row, Col, Spinner } from 'react-bootstrap';
import { useFilePicker, Validator } from 'use-file-picker';
import { AppContext } from '../index';
import {Content,  NamedEntity, entity_color_mapping} from '../models/Content';
import { ContentElement } from './ContentElement';

interface FilesParserStats {
    "total_contents": number,
    "total_messages": number,
    "duplicate_content": number,
    "error": string,
    "processed_contents": number,
    "processed_messages": number,
}

export interface ModelSpecs {
    "classification": ClassificationModelSpecs[],
    "ner": NerModelSpecs[]
}

export interface ClassificationModelSpecs {
    name: string;
    path: string;
    task: string;
    description?: string;
    size: string;
    default: boolean;
    default_hypothesis: string;
}

export interface NerModelSpecs {
    name: string;
    path: string;
    task: string;
    description?: string;
    size: string;
    default: boolean;
}

interface Mapping {
    content_identifier_column: string;
    content_column: string;
    path_column: string;
    attribute_type_column: string;
    attribute_types_to_keep: string[];
    attribute_types_to_analyze: string[];
}


function FilesParserForm() {
    const [hypothesisTemplate, setHypothesisTemplate] = React.useState("The topic of this text is about {}.");
    const [labels, setLabels] = React.useState("drugs,hacking,fraud,counterfeit goods,cryptocurrency,delivery,weapons");
    const [path, setPath] = React.useState("");
    const [useRecursive, setUseRecursive] = React.useState(false);
    const [content, setContent] = React.useState() as [[Content], any];
    const [stats, setStats] = React.useState() as FilesParserStats | any;
    const [availableModels, setAvailableModels] = React.useState<ModelSpecs>();
    const [classificationModel, setClassificationModel] = React.useState<ClassificationModelSpecs>();
    const [nerModel, setNerModel] = React.useState<NerModelSpecs>();
    const [showModelSelection, setShowModelSelection] = React.useState(false);
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [saveFiles, setSaveFiles] = React.useState(true);
    const [fileType, setFileType] = React.useState("html");
    const [mapping, setMapping] = React.useState<Mapping>({
        content_identifier_column: "",
        content_column: "",
        path_column: "",
        attribute_type_column: "",
        attribute_types_to_keep: [],
        attribute_types_to_analyze: []
    });
    const [supportedFileTypes, setSupportedFileTypes] = React.useState([{name: "html", requireMapping: false}, {name: "csv", requireMapping: true}]);
    const { server_ip, server_port, server_api } = React.useContext(AppContext);
    
    React.useEffect(() => {
        console.log("Fetching available models");
        // fetch available models from server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_files_parser`)
            .then(response => response.json())
            .then(data => { 
                data = JSON.parse(data);
                console.log(data);
                let models: ModelSpecs = data.models;
                setAvailableModels(models);
                // find default models
                let defaultClassificationModel = models.classification.find(model => model.default);
                let defaultNerModel = models.ner.find(model => model.task === "ner" && model.default);
                if (defaultClassificationModel) {
                    setClassificationModel(defaultClassificationModel);
                    setHypothesisTemplate(defaultClassificationModel.default_hypothesis);
                }
                if (defaultNerModel) {
                    setNerModel(defaultNerModel);
                }
            });
    }, []);


    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        console.log(`Hypothesis Template: ${hypothesisTemplate} Labels: ${labels} Path: ${path} Use Recursive: ${useRecursive}`);
        setIsSubmitting(true);
        
        if (mapping.attribute_types_to_keep.length > 0) {
            mapping.attribute_types_to_keep = mapping.attribute_types_to_keep.map((type) => type.trim());
        }

        if (mapping.attribute_types_to_analyze.length > 0) {
            mapping.attribute_types_to_analyze = mapping.attribute_types_to_analyze.map((type) => type.trim());
        }

        // Construct the request body, which is a JSON object
        const requestBody = {
            "hypothesis_template": hypothesisTemplate,
            "labels": labels.split(','),
            "path": path,
            "recursive": useRecursive,
            "save": saveFiles,
            "models": {
                "classification": classificationModel?.name,
                "ner": nerModel?.name
            },
            "file_type": fileType,
            "mapping": mapping
        };

        // Send the request to the server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_files_parser`, {
            // wait forever for the response
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody),
        })
        .then(response => response.json(), error => console.log("Error: " + error))
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            console.log('Success:', data);
            let contents: Content[] = data.contents;
            let stats: FilesParserStats = data.stats;
            setContent(contents);
            setStats(stats);

        }, error => console.log("Error: " + error)
        ).finally(() => {
            setIsSubmitting(false);
        });
    }

    return (
        <Container className="bg-none" >
            <Stack gap={3} className="mt-4 text-light">
                <Form onSubmit={handleSubmit}>
                    <Form.Switch className="mb-2" label="Show Model Selection" checked={showModelSelection} onChange={(e) => setShowModelSelection(e.target.checked)} />
                    {/* Model selection */}
                    {showModelSelection && availableModels &&
                        <Stack gap={3} direction="vertical">
                            <Form.Group className="mb-1" controlId="formModel">
                                <Form.Label className='text-light'>Classification Model</Form.Label>
                                <Form.Select aria-label="Default select example" value={classificationModel?.name} onChange={(e) => {
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
                                <Form.Select aria-label="Default select example" value={nerModel?.name} onChange={(e) => setNerModel(
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
                        <Form.Control type="string" placeholder="Enter hypothesis template in the form: My hypothesis {}." value={hypothesisTemplate} onChange={(e) => setHypothesisTemplate(e.target.value)}/>
                        <Form.Text className="text-muted">
                            At inference time, labels will be placed inside the {"{}"}.
                        </Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3" controlId="formLabels">
                        <Form.Label className='text-light'>Labels</Form.Label>
                        <Form.Control type="string" placeholder="Enter labels separated by ',' symbol." value={labels} onChange={(e) => setLabels(e.target.value)}/>
                    </Form.Group>

                    {/* selector for supported file types */}
                    <Form.Group className="mb-3 w-25" controlId="formFileType">
                        <Form.Label className='text-light'>File Type</Form.Label>
                        <Form.Select aria-label="Default select example" value={fileType} onChange={(e) => setFileType(e.target.value)}>
                            { supportedFileTypes.map((fileType, index) => {
                                return <option key={index} value={fileType.name}>{fileType.name}</option>
                            })}
                        </Form.Select>
                    </Form.Group>
                    {/** Mapping for file types that require it (create one input for each attribute type)
                     * {
                            "content_identifier_column": "InstanceId",
                            "content_column": "Content",
                            "path_column": "UrlPath",
                            "attribute_type_column": "AttributeTag",
                            "attribute_types_to_keep": ["content", "author_name"],
                            "attribute_types_to_analyze": ["content"] 
                        }
                     */}
                    { supportedFileTypes.find((item) => item.name == fileType)?.requireMapping &&
                        <Form.Group className="mb-3 w-50" controlId="formMapping">
                            <Stack gap={1} direction="vertical">
                                <Form.Label className='text-light'>Column/Attribute Mapping</Form.Label>
                                <Form.Text className="text-muted">
                                    Column name that contains the content identifier.
                                </Form.Text>
                                <Form.Control type="string" placeholder="content_identifier_column" value={mapping.content_identifier_column} onChange={(e) => setMapping({...mapping, content_identifier_column: e.target.value})}/>
                                <Form.Text className="text-muted">
                                    Column name that contains the textual content.
                                </Form.Text>
                                <Form.Control type="string" placeholder="content_column" value={mapping.content_column} onChange={(e) => setMapping({...mapping, content_column: e.target.value})}/>
                                <Form.Text className="text-muted">
                                    Column name that contains the attribute type (tag for authors, titles, messages etc.)
                                </Form.Text>
                                <Form.Control type="string" placeholder="attribute_type_column" value={mapping.attribute_type_column} onChange={(e) => setMapping({...mapping, attribute_type_column: e.target.value})}/>
                                <Form.Text className="text-muted">
                                    Attribute types to keep. These attributes will be included within the final Content object.
                                </Form.Text>
                                <Form.Control type="string" placeholder="attribute_types_to_keep" value={mapping.attribute_types_to_keep} onChange={(e) => setMapping({...mapping, attribute_types_to_keep: e.target.value.split(',')})}/>
                                <Form.Text className="text-muted">
                                    Attribute types to analyze. These attributes will be analyzed by the NLP models and will contain categories or named entities.
                                </Form.Text>
                                <Form.Control type="string" placeholder="attribute_types_to_analyze" value={mapping.attribute_types_to_analyze} onChange={(e) => setMapping({...mapping, attribute_types_to_analyze: e.target.value.split(',')})}/>
                                <Form.Text className="text-muted">
                                    Column name that contains the path to the original file or URL. (optional)
                                </Form.Text>
                                <Form.Control type="string" placeholder="path_column" value={mapping.path_column} onChange={(e) => setMapping({...mapping, path_column: e.target.value})}/>
                            </Stack>
                        </Form.Group>
                    }

                    <Form.Group className="mb-3" controlId="formPaths">
                        <Form.Label className='text-light'>Path to Files</Form.Label>
                        <Form.Control type="string" placeholder="Enter path to files to be parsed or select files/directory."
                                      value={path} onChange={(e) => setPath(e.target.value)}/>
                    </Form.Group>


                    <Stack direction='vertical' gap={1}>
                            <Form.Group className="mb-3" controlId="formUseRecursive">
                                <Form.Check type="checkbox" label="Use reccursive path resolution" className='text-light' checked={useRecursive} onChange={(e) => setUseRecursive(e.target.checked)}/>
                            </Form.Group>
                            <Form.Group className="mb-3" controlId="formSaveFiles">
                                <Form.Check type="checkbox" label="Save files to the database" className='text-light' checked={saveFiles} onChange={(e) => setSaveFiles(e.target.checked)}/>
                            </Form.Group>
                    </Stack>

                    <Button variant="primary" type="submit" className='w-25 mb-5' disabled={isSubmitting}>
                        {isSubmitting && <Spinner animation="border" size="sm" />}
                        {!isSubmitting && <span>Submit</span>}
                    </Button>
                </Form>
                {
                    stats &&
                    <Container className='text-light mb-3 mt-3'>
                        <h3>Stats:</h3>
                        <div className='text-light mt-3'>Total content: {stats.total_contents}</div>
                        <div className='text-light mt-3'>Total messages {stats.total_messages}</div>
                        <div className='text-light mt-3'>Total content processed: {stats.processed_contents}</div>
                        <div className='text-light mt-3'>Total messages processed: {stats.processed_messages}</div>
                        <div className='text-light mt-3'>Total duplicate content: {stats.duplicate_content}</div>
                        <div className='text-light mt-3'>Total errors while parsing: {stats.error}</div>
                    </Container>
                }
                {
                    content &&
                    content.map((item, index) => {
                        return (
                            <ContentElement key={index} content={item}  />
                        );
                        }
                    )
                }

            </Stack>
        </Container>
    );
}

export default FilesParserForm;