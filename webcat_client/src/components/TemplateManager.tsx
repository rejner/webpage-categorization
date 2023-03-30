import React, { useState, useEffect, useContext } from 'react';
import { Container, Button, Form, Row, Col, Spinner, Table } from 'react-bootstrap';
import { AppContext } from '..';
import { colorToSectionMapping } from './Templater';
import { Template, Template_v2 } from '../models/Template';
import { Element } from '../models/Element';


function TemplateManager() {

    const [templates, setTemplates] = useState<Template[]>();
    const [templates_v2, setTemplates_v2] = useState<Template_v2[]>([]);
    const [isLoading, setLoading] = useState(false);
    const {server_ip, server_port, server_api} = useContext(AppContext);
    
    function fetch_templates(version: number) {
        setLoading(true);
        // get request to the server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates/manager?` + new URLSearchParams('version=' + version)
        ).then(response => response.json())
        .then(data => {
                console.log(JSON.parse(data));
                if (version == 1)
                    setTemplates(JSON.parse(data));
                else
                    setTemplates_v2(JSON.parse(data));
                setLoading(false);
            });
    }


    // fetch templates from the server
    useEffect(() => {
        fetch_templates(1);
        fetch_templates(2);
    }, []);

    function deleteTemplate(id: number, version: number) {
        // delete request to the server
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_templates/manager`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'id': id, 'version': version})
        })
        .then(response => response.json())
        .then(data => {
            fetch_templates(version);
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
                    templates.map((template: Template, index) => {
                        return (
                            <tr key={index}>
                                <td>
                                    <ul>
                                        <li>Id: {template.id}</li>
                                        <li>File: {template.origin_file}</li>
                                        <li>Creation Date: {template.creation_date}</li>
                                        <li>Version: 1</li>
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
                                    <Button variant='danger' onClick={() => deleteTemplate(template.id, 1)}>Delete</Button>
                                </td>
                            </tr>
                        );
                    })
                }

                { templates_v2 &&
                    templates_v2.map((template: Template_v2, index) => {
                        return (
                            <tr key={index}>
                                <td>
                                    <ul>
                                        <li>Id: {template.id}</li>
                                        <li>File: {template.origin_file}</li>
                                        <li>Creation Date: {template.creation_date}</li>
                                        <li>Version: 2</li>
                                    </ul>

                                </td>
                                <td>
                                    {
                                        template.elements.map((element, index) => {
                                            return (
                                                <ul key={index}>
                                                    <li>Type: {element.type}</li>
                                                    <li>Tag: {element.tag}</li>
                                                    <li>Parent Tag: {element.parent_tag}</li>
                                                    <li>Grandparent Tag: {element.grandparent_tag}</li>
                                                    <li>Depth: {element.depth}</li>
                                                </ul>
                                            );
                                        })
                                    }
                                </td>
                                <td>
                                    <Button variant='danger' onClick={() => deleteTemplate(template.id, 2)}>Delete</Button>
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
