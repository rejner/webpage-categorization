import React, { useState, useEffect, useContext } from 'react';
import { Container, Button, Form, Row, Col, Spinner } from 'react-bootstrap';
import { useFilePicker } from 'use-file-picker';
import { RenderElement, SectionTemplate } from './RenderElement';
import { AppContext } from '..';
import { colorToSectionMapping } from './Templater';

interface Templates{
    'post-area': SectionTemplate[];
    'author': SectionTemplate[] | null;
    'post-header': SectionTemplate[] | null;
    'post-body': SectionTemplate[];
}


function TemplateManager() {

    const [templates, setTemplates] = useState<Templates>();
    const [isLoading, setLoading] = useState(false);
    const {server_ip, server_port, server_api} = useContext(AppContext);
    
    // fetch templates from the server
    useEffect(() => {
        setLoading(true);
        console.log(`http://${server_ip}:${server_port}${server_api}/webcat_templates`);
        // get request to the server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates`)
            .then(response => response.json())
            .then(data => {
                console.log(JSON.parse(data));
                
                setTemplates(JSON.parse(data));
                setLoading(false);
            });
    }, []);

    return (
    <>
        <h3 className='mt-3 text-light'>Template Manager</h3>
        {
            
            // create a list of templates (interface Template)
            // each template should have a button to delete it
            // each template should have a button to edit it
            // each template should have a button to view it

            isLoading || !templates ?
            <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
            </Spinner>
            :
            <Container>
                <Row>
                    <Col>
                        <h4 className='mt-3 text-light'>Post Area</h4>
                        {
                            templates['post-area'].map((template, index) => {
                                return (
                                    <div key={index} className='text-light'>
                                        <p>{template.tag}</p>
                                        <p>{template.id}</p>
                                        <p>{template.classes}</p>
                                        <Button variant='danger'>Delete</Button>
                                    </div>
                                    
                                );
                            })
                        }
                    </Col>
                    <Col>
                        <h4 className='mt-3 text-light'>Author</h4>
                        {
                            templates['author'] ?
                            templates['author'].map((template, index) => {
                                return (
                                    <div key={index} className='text-light'>
                                        <p>{template.tag}</p>
                                        <p>{template.id}</p>
                                        <p>{template.classes}</p>
                                        <Button variant='danger'>Delete</Button>
                                    </div>
                                    
                                );
                            })
                            :
                            <p>No templates</p>
                        }
                    </Col>
                    <Col>
                        <h4 className='mt-3 text-light'>Post Header</h4>
                        {
                            templates['post-header'] ?
                            templates['post-header'].map((template, index) => {
                                return (
                                    <div key={index} className='text-light'>
                                        <p>{template.tag}</p>
                                        <p>{template.id}</p>
                                        <p>{template.classes}</p>
                                        <Button variant='danger'>Delete</Button>
                                    </div>
                                    
                                );
                            })
                            :
                            <p>No templates</p>
                        }
                    </Col>
                    <Col>
                        <h4 className='mt-3 text-light'>Post Body</h4>
                        {
                            templates['post-body'].map((template, index) => {
                                return (
                                    <div key={index} className='text-light'>
                                        <p>{template.tag}</p>
                                        <p>{template.id}</p>
                                        <p>{template.classes}</p>
                                        <Button variant='danger'>Delete</Button>
                                    </div>
                                    
                                );
                            })
                        }
                    </Col>
                </Row>
            </Container>                       
        }
    
    </>                           
    );

}

export default TemplateManager;
