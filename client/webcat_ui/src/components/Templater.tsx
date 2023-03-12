// This React component will inject webpage content into itself and will act like a google chrome devtools.
// User can move with mouse and click on elements to get their css selectors.

import React, { useState, useEffect } from 'react';
import { Container, Button, Form, Row, Col, Spinner } from 'react-bootstrap';
import { useFilePicker } from 'use-file-picker';
import { RenderElement, SectionTemplate } from './RenderElement';
import { AppContext } from '..';


export const colorToSectionMapping: {[key: string]: string} = {
    primary: "post-area",
    secondary: "author",
    success: "post-header",
    // danger: "post-footer",
    warning: "post-body",
    //info: "post-author",
    //light: "post-content",
}

interface ControlsContextInterface {
    selectedLabel: string,
    setSelectedLabel: React.Dispatch<React.SetStateAction<string>>,
    unrollAll: boolean,
    setUnrollAll: React.Dispatch<React.SetStateAction<boolean>>
}

// create context for controls
export const ControlsContext = React.createContext<ControlsContextInterface>({
    selectedLabel: "warning",
    setSelectedLabel: () => {},
    unrollAll: false,
    setUnrollAll: () => {},
});

interface TemplatesContextInterface {
    createTemplate: boolean,
    setCreateTemplate: React.Dispatch<React.SetStateAction<boolean>>,
    templates: SectionTemplate[],
    addTemplate: (template: SectionTemplate) => void,
}


// Create array of objects, which will be served as context for child components
export const TemplatesContext = React.createContext<TemplatesContextInterface>({
    createTemplate: false,
    setCreateTemplate: () => {},
    templates: [],
    addTemplate: (template: SectionTemplate) => {
        
    }
});


function Templater() {

    // load file /workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-10-20/viewtopic.php_pid=1108 into DOM object
    const [openFileSelector, { filesContent, loading, errors, plainFiles, clear }] = useFilePicker({
        multiple: false,
        readAs: 'Text',
    });
    // document will be an instance of HTMLDocument
    const [doc, setDoc] = useState<Document>(); 
    const [selectedLabel, setSelectedLabel] = useState<string>("warning");
    const [unrollAll, setUnrollAll] =  useState<boolean>(false);
    const [createTemplate, setCreateTemplate] = useState<boolean>(false);
    const [templates, setTemplates] = useState<SectionTemplate[]>([]);
    const { server_ip, server_port, server_api } = React.useContext(AppContext);
    const addTemplate = (template: SectionTemplate) => {
        console.log("adding template -- top of function");
        console.log(templates);
        templates.push(template);
        console.log(templates);
        console.log("adding template -- bottom of function");
    }
    // use context to pass selectedLabel to child components

    useEffect(() => {
        if (filesContent.length > 0) {
          const parser = new DOMParser();
          let document = parser.parseFromString(filesContent[0].content, 'text/html');
        //   const elements = document.querySelectorAll('meta, script, style, link, head');
        //   elements.forEach(element => element.remove());
        //   const textNodes = document.querySelectorAll('text');
        //   textNodes.forEach(textNode => {
        //     if (textNode.textContent && !textNode.textContent.trim()) {
        //       textNode.remove();
        //     }
        //   });
          setDoc(document);
        }
      }, [filesContent]);

    useEffect(() => {
    if (templates.length > 0) {
        // get index of last template
        let index = templates.length - 1;
        // get last template
        let lastTemplate = templates[index];
        if (lastTemplate.type === "none") {
            // if last template is of type none, remove it
            templates.pop();
        }
    }
    }, [templates]);


      return (
        <TemplatesContext.Provider value={{createTemplate, setCreateTemplate, templates, addTemplate: addTemplate}}>
            <ControlsContext.Provider value={{selectedLabel, setSelectedLabel, unrollAll, setUnrollAll}}>
                <h3 className='mt-3 text-light'>Template Maker</h3>
                <Button onClick={openFileSelector} className="mt-3 w-25">Select File</Button>
                    
                {/* Create 5 labels which can be selected (they behave like checkbox) in primary, warning etc. colors. */}

                <Row className='mt-0'>
                    {
                        ['primary', 'secondary', 'success', 'warning'].map((variant, idx) => (
                        <Col key={'button-wrap-col-' + idx.toString()}>
                            {
                            (selectedLabel === variant) ? 
                                    <Button key={'button-type-' + idx.toString()} variant={variant} onClick={() => setSelectedLabel(variant)} 
                                            className="mt-3" style={{width: "10vw"}}>{colorToSectionMapping[variant]}</Button>
                                :
                                    <Button key={'button-type-' + idx.toString()} variant={variant} onClick={() => setSelectedLabel(variant)} 
                                            className="mt-3 text-light" style={{width: "10vw", background: 'none'}}>{colorToSectionMapping[variant]}</Button>
                                
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
                        <RenderElement el={doc.body} depth={0} />
                    </Container>
                }
                </Container>
                
                <Row className="mt-3">
                    <Button onClick={() => {setCreateTemplate(true);
                    // set timeout to wait for templates to be added and re-rendered
                    setTimeout(() => {
                        console.log("Templates:" + templates);
                        const newTemplates = [...templates];
                        setTemplates(newTemplates);
                        setCreateTemplate(false);
                    }, 1000);
                    
                    }} className="mt-3 w-25">
                        {/* Spinning circle when createTemplate == true */}
                        {createTemplate && <Spinner animation="border" size="sm" />}
                        {!createTemplate && <span>Create Template</span>}
                        </Button>
                    {/* Add separator 20px width */}
                    <div style={{width: "20px"}}></div>
                    <Button variant='danger' onClick={() => {setCreateTemplate(false); setTemplates([])}} className="mt-3 w-25">Clear Templates</Button>
                    <div style={{width: "20px"}}></div>
                    {/*  Send to server button */}
                    { templates.length > 1 &&
                        <Button variant='success' className="mt-3 w-25" onClick={() => {
                            console.log("Sending templates to server");
                            console.log(templates);
         

                            fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(
                                    {
                                        'templates': JSON.stringify(templates)
                                    }
          
                                    )
                            })
                            .then(response => response.json())
                            .then(data => {
                                console.log('Success:', data);
                            })
                            .catch((error) => {
                                console.error('Error:', error);
                            });
                            }} >
                            {/* Spinning circle when createTemplate == true */}
                            {createTemplate && <Spinner animation="border" size="sm" />}
                            {!createTemplate && <span>Save Templates</span>}
                        </Button>
                    }
                </Row>

                {/* Display content of templates is not empty */}
                <Container className="bg-none text-light mt-1 mb-5 h-25 overflow-auto border-bottom border-dark">
                    {templates.length > 0 && <h4>Templates Preview</h4>}
                    {templates.length > 0 && templates.map((template, idx) => (
                        <div key={'template-wrap-' + idx.toString()}>
                            <h5>{template.type}</h5>
                            <ul>
                                {Object.keys(template).map((section, attr_idx) => (
                                    <li key={`template-${idx}-${attr_idx}`}>{section}: {Object.values(template)[idx]}</li>
                                ))}
                            </ul>
                        </div>
                    ))}
                
                </Container>
            </ControlsContext.Provider>
        </TemplatesContext.Provider>
      );

}

export default Templater;
