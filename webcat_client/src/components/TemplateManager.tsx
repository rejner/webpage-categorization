import React, { useState, useEffect, useContext } from 'react';
import { Container, Button, Form, Row, Col, Spinner, Table } from 'react-bootstrap';
import { AppContext } from '..';
import { colorToSectionMapping } from './Templater';
import { Template } from '../models/Template';
import { Element } from '../models/Element';


function TemplateManager() {

    const [templates, setTemplates] = useState<Template[]>();
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

    function deleteTemplate(id: number) {
        // delete request to the server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'id': id})
        })
        .then(response => response.json())
        .then(data => {
            // fetch updated templates
            fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates`)
                .then(response => response.json())
                .then(data => {
                    console.log(JSON.parse(data));
                    
                    setTemplates(JSON.parse(data));
                    setLoading(false);
                });
        });
    };

    return (
    <>
        <h3 className='mt-3 text-light'>Template Manager</h3>
        <hr className='bg-light'/>
        {/* Create the same with Table */}
        <Table striped bordered hover variant="dark">
            <thead>
                <tr>
                    <th>Origin File</th>
                    <th>Elements</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                { templates &&
                    templates.map((template, index) => {
                        return (
                            <tr key={index}>
                                <td>
                                    <ul>
                                        <li>Id: {template.id}</li>
                                        <li>File: {template.origin_file}</li>
                                        <li>Creation Date: {template.creation_date}</li>
                                    </ul>

                                </td>
                                <td>
                                    {
                                        template.elements.map((element, index) => {
                                            return (
                                                <ul key={index}>
                                                    <li>Type: {element.type}</li>
                                                    <li>Tag: {element.tag}</li>
                                                    <li>Id: {element.id_attr}</li>
                                                    <li>Classes: {element.classes.join(', ')}</li>
                                                </ul>
                                            );
                                        })
                                    }
                                </td>
                                <td>
                                    <Button variant='danger' onClick={() => deleteTemplate(template.id)}>Delete</Button>
                                </td>
                            </tr>
                        );
                    })
                }
            </tbody>
        </Table>
        




    
    </>                           
    );

}

export default TemplateManager;
