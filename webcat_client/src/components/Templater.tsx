// This React component will inject webpage content into itself and will act like a google chrome devtools.
// User can move with mouse and click on elements to get their css selectors.

import React, { useState, useEffect } from 'react';
import { Container, Button, Form, Row, Col, Spinner, Stack } from 'react-bootstrap';
import { useFilePicker } from 'use-file-picker';
import { RenderElement } from './RenderElement';
import { AppContext } from '..';
import { Template } from '../models/Template';
import { Element, ElementType } from '../models/Element';


const availableColors = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"];

interface ControlsContextInterface {
    selectedElementType: ElementType | undefined,
    setSelectedElementType: React.Dispatch<React.SetStateAction<ElementType | undefined>>,
    unrollAll: boolean,
    setUnrollAll: React.Dispatch<React.SetStateAction<boolean>>,
    elementTypeColors: {[key: string]: string},
    setElementTypeColors: React.Dispatch<React.SetStateAction<{[key: string]: string}>>,
}

// create context for controls
export const ControlsContext = React.createContext<ControlsContextInterface>({
    selectedElementType: undefined,
    setSelectedElementType: () => {},
    unrollAll: false,
    setUnrollAll: () => {},
    elementTypeColors: {},
    setElementTypeColors: () => {},
});

interface TemplatesContextInterface {
    createTemplate: boolean,
    setCreateTemplate: React.Dispatch<React.SetStateAction<boolean>>,
    elements: Element[],
    addElement: (template: Element) => void,
}


// Create array of objects, which will be served as context for child components
export const TemplatesContext = React.createContext<TemplatesContextInterface>({
    createTemplate: false,
    setCreateTemplate: () => {},
    elements: [],
    addElement: (template: Element) => {
        
    }
});


function Templater() {
    const [openFileSelector, { filesContent, loading, errors, plainFiles, clear }] = useFilePicker({
        multiple: false,
        readAs: 'Text',
    });
    const [doc, setDoc] = useState<Document>(); 
    // const [selectedLabel, setSelectedLabel] = useState<string>("warning");
    const [selectedElementType, setSelectedElementType] = useState<ElementType>();
    const [unrollAll, setUnrollAll] =  useState<boolean>(false);
    const [createTemplate, setCreateTemplate] = useState<boolean>(false);
    const [elements, setElements] = useState<Element[]>([]);
    const [elementTypes, setElementTypes] = useState<ElementType[]>([]);
    const [template, setTemplate] = useState<Template>();
    const [elementTypeColors, setElementTypeColors] = useState<{[key: string]: string}>({});
    const { server_ip, server_port, server_api } = React.useContext(AppContext);
    const addElementToTemplate = (element: Element) => {
        console.log("adding template -- top of function");
        console.log(elements);
        elements.push(element);
        console.log(elements);
        console.log("adding template -- bottom of function");
    }
    // fetch element_types from server
    useEffect(() => {
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates/element_types` ).then(response => {
            if (response.status === 200) {
                return response.json();
            }
        }).then(data => {
            let els: ElementType[] = JSON.parse(data);
            setElementTypes(els);
        }).catch(error => {
            console.log(error);
        });
    }, []);

    useEffect(() => {
        // create color mapping for all element types (multiple element types can have same color)
        let tagTocolorMapping: {[key: string]: string} = {};
        for (let i = 0; i < elementTypes.length; i++) {
            let color = availableColors[i % availableColors.length];
            if (tagTocolorMapping[elementTypes[i].tag] === undefined) {
                tagTocolorMapping[elementTypes[i].tag] = color;
            }
        }
        console.log(tagTocolorMapping);
        setElementTypeColors(tagTocolorMapping);
    }, [elementTypes]);

    useEffect(() => {
        console.log("selectedElementType changed");
        console.log(selectedElementType);
    }, [selectedElementType]);

    // use context to pass selectedLabel to child components
    useEffect(() => {
        if (filesContent.length > 0) {
          const parser = new DOMParser();
          let document = parser.parseFromString(filesContent[0].content, 'text/html');
          setDoc(document);
        }
      }, [filesContent]);

    useEffect(() => {
    if (elements.length > 0) {
        // get index of last template
        let index = elements.length - 1;
        // get last template
        let lastTemplate = elements[index];
        if (lastTemplate.type === undefined) {
            // if last template is of type none, remove it
            elements.pop();
        }
    }
    }, [elements]);

    function sendTemplate() {
        console.log("Sending template to server");
        console.log(template);
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates/templates`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
                {
                    template: template,
                    version: 2,
                }
            )
        }).then(response => {
            console.log(response);
            if (response.status === 200) {
                console.log("Template sent successfully");
                alert("Template saved successfully!");
            }
        }).catch(error => {
            console.log(error);
            alert("Error while saving template!");
        });
    }

      return (
        <TemplatesContext.Provider value={{createTemplate, setCreateTemplate, elements, addElement: addElementToTemplate}}>
            <ControlsContext.Provider value={{selectedElementType, setSelectedElementType, unrollAll, setUnrollAll, elementTypeColors, setElementTypeColors}}>
                <h3 className='mt-3 text-light'>Template Maker</h3>
                <Button onClick={openFileSelector} className="mt-3 w-25">Select File</Button>
                <Stack className="mt-3" direction="horizontal" gap={3}>
                {doc && 
                    <Button onClick={() => {setCreateTemplate(true);
                    // set timeout to wait for elements to be added and re-rendered
                    setTimeout(() => {
                        console.log("Templates:" + elements);
                        const newElements = [...elements];
                        setElements(newElements);
                        let newTemplate: Template = {
                            'id': 0,
                            'creation_date': new Date().toISOString(),
                            'origin_file': plainFiles[0].name,
                            'elements': elements
                        };
                        setTemplate(newTemplate);
                        setCreateTemplate(false);
                    }, 1000);
                    
                    }} className="mt-3 w-25">
                        { createTemplate ? <Spinner animation="border" size="sm" /> : <span>Create Template</span> }
                    </Button>
                    }
                    {/* Add separator 20px width */}
                    {
                        doc && !createTemplate &&
                        <>
                            <Button variant='danger' onClick={() => {setCreateTemplate(false); setElements([]); setTemplate(undefined)}} className="mt-3 w-25">Clear Templates</Button>
                        </>
                    }
                    
                    
                    {/*  Send to server button */}
                    { elements.length > 1 &&
                        <Button variant='success' className="mt-3 w-25" onClick={() => sendTemplate()}>
                            {!createTemplate && <span>Save Templates</span>}
                        </Button>
                    }
                </Stack>
                    
                {/* Create 5 labels which can be selected (they behave like checkbox) in primary, warning etc. colors. */}

                <Row className='mt-0'>
                    { elementTypes && elementTypes.length > 0 &&
                        elementTypes.map((type, idx) => (
                            <Col key={'button-wrap-col-' + idx.toString()}>
                                {
                                (selectedElementType === type) ?
                                        <Button key={'button-type-' + idx} variant={elementTypeColors[selectedElementType.tag]} onClick={() => setSelectedElementType(type)}
                                                className="mt-3" style={{width: "10vw"}}>{type.name}</Button>
                                    :
                                        <Button key={'button-type-' + idx} variant={elementTypeColors[type.tag]} onClick={() => setSelectedElementType(type)}
                                                className="mt-3 text-light" style={{width: "10vw", background: 'none'}}>{type.name}</Button>
                                }
                            </Col>
                        ))
                    }
                    {/* Create "Unroll all" checkbox */}
                    <Col key={"button-wrap-col-checkbox"}>
                        <Form.Check key="okokok" type="checkbox" id="custom-switch" label="Unroll All" className="mt-3" style={{width: "10vw", color: "white"}}
                                    onChange={() => setUnrollAll(!unrollAll)} />
                    </Col>
                </Row>

                <Container>
                    {!doc && <h4 className='text-light mt-4'>Select file to be parsed...</h4>}
                {doc &&
                    <Container className="bg-none text-light mt-1 h-25 overflow-auto border-bottom border-dark" style={{maxHeight: "60vh", minHeight: "60vh"}}>
                        <RenderElement el={doc.body} depth={1} />
                    </Container>
                }
                </Container>


                {/* Display content of template is not empty */}
                <Container className="bg-none text-light mt-1 mb-5 h-25 overflow-auto border-bottom border-dark">
                    { template && <h4>Template Preview</h4>}
                    { template && <div>
                        <h6>Template ID: {template.id}</h6>
                        <h6>Creation Date: {template.creation_date}</h6>
                        <h6>Origin File: {template.origin_file}</h6>
                        <h6>Elements:</h6>
                        <ul>
                            {template.elements.map((element, idx) => {
                                {/* array of string into one string with , separator */}
                                return <li key={idx.toString()}>{element.type.tag} ({element.type.analysis_flag ? 'true' : 'false'}) - {element.xPath} classes: {element.classes}</li>
                            })}

                        </ul>
                        </div>}
                
                </Container>
            </ControlsContext.Provider>
        </TemplatesContext.Provider>
      );

}

export default Templater;
