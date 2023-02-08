// This React component will inject webpage content into itself and will act like a google chrome devtools.
// User can move with mouse and click on elements to get their css selectors.

import React, { useState, useEffect } from 'react';
import { Stack, Container, Button, Form, Row, Col } from 'react-bootstrap';
import { useFilePicker, Validator } from 'use-file-picker';
import { useLocation } from 'react-router-dom';
import { format } from 'path';
import RenderElement from './RenderElement';

const colorToSectionMapping: {[key: string]: string} = {
    primary: "post",
    secondary: "title",
    success: "post-header",
    danger: "post-footer",
    warning: "post-body",
    info: "post-author",
    light: "post-content",
}

interface ControlsContextInterface {
    selectedLabel: string,
    setSelectedLabel: React.Dispatch<React.SetStateAction<string>>
}

// create context for controls
export const ControlsContext = React.createContext<ControlsContextInterface>({
    selectedLabel: "warning",
    setSelectedLabel: () => {}
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
    // use context to pass selectedLabel to child components

    useEffect(() => {
        if (filesContent.length > 0 && !doc) {
          const parser = new DOMParser();
          let document = parser.parseFromString(filesContent[0].content, 'text/html');
          const elements = document.querySelectorAll('meta, script, style, link, head');
          elements.forEach(element => element.remove());
          const textNodes = document.querySelectorAll('text');
          textNodes.forEach(textNode => {
            if (textNode.textContent && !textNode.textContent.trim()) {
              textNode.remove();
            }
          });
          setDoc(document);
        }
      }, [filesContent, doc]);

      return (
        <ControlsContext.Provider value={{selectedLabel, setSelectedLabel}}>
            <h3 className='mt-3 text-light'>Template Maker</h3>

            <Container>
                {!doc && <h4 className='text-light mt-1'>Select file to be parsed:</h4>}
            {doc &&
                <Container className="bg-none text-light mt-1 h-25 overflow-auto border-bottom border-dark" style={{maxHeight: "60vh", minHeight: "60vh"}}>
                    <RenderElement el={doc.body} depth={0} />
                </Container>
            }
            
            <Button onClick={openFileSelector} className="mt-3">Open File</Button>
            {/* Create 5 labels which can be selected (they behave like checkbox) in primary, warning etc. colors. */}

            <Row>
                    {
                        ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light'].map((variant, idx) => (
                        <>
                        <Col>
                            {
                            (selectedLabel === variant) ? 
                                    <Button key={idx} variant={variant} onClick={() => setSelectedLabel(variant)} 
                                            className="mt-3" style={{width: "10vw"}}>{colorToSectionMapping[variant]}</Button>
                                :
                                    <Button key={idx} variant={variant} onClick={() => setSelectedLabel(variant)} 
                                            className="mt-3 text-light" style={{width: "10vw", background: 'none'}}>{colorToSectionMapping[variant]}</Button>
                                
                            }
    
                        </Col>
                        </>
                        ))
                    }
            </Row>
            </Container>
        </ControlsContext.Provider>
      );

}

export default Templater;
