import React from 'react';
import { Stack, Container, Button, Form, Row, Col } from 'react-bootstrap';
import { AppContext } from '../index';
import {Content, entity_color_mapping} from '../models/Content';

interface WebCatFilters {
    categories: string[],
    cat_threshold: number,
    entity_types: string[],
    ent_threshold: number,
    entity_values: string[],
    file_names: string[],
    file_paths: string[],
}

interface WebCatInfo {
    categories: string[],
    entity_types: string[],
}

function DataViewer() {
    const [categories, setCategories] = React.useState() as [string[], (categories: string[]) => void];
    const [entity_types, setEntityTypes] = React.useState() as [string[], (entity_types: string[]) => void];
    const [content, setContent] = React.useState() as [Content[], (content: Content[]) => void];
    const [filter, setFilter] = React.useState<WebCatFilters>({
        categories: [],
        cat_threshold: 0.0,
        entity_types: [],
        ent_threshold: 0.0,
        entity_values: [],
        file_names: [],
        file_paths: [],
    });

    // Read server_ip and server_port from the context
    const { server_ip, server_port, server_api } = React.useContext(AppContext);

    // fetch categories and entity types
    React.useEffect(() => {
        if (categories && entity_types) {
            return;
        }
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_data_provider`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(response => response.json(), error => console.log("Error: " + error))
        .then(data => {
            console.log('Success:', data);
            if (data.error) {
                alert(data.error)
                return;
            } 

            let info: WebCatInfo = data;
            setCategories(info.categories);
            setEntityTypes(info.entity_types);
            
        }, error => console.log("Error: " + error)
        )
    }, []);

    function request_content() {
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_data_provider`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(filter)
        })
        .then(response => response.json(), error => console.log("Error: " + error))
        .then(data => {
            console.log('Success:', data);
            if (data.error) {
                alert(data.error)
                return;
            }
            let contents: Content[] = data;
            for (let c of contents) {
                if (c.entities.length === 0) {
                    continue;
                }
                for (let entity of c.entities) {
                    // replace entity with <span> tag
                    c.text = c.text.replace(entity.name, `<span class='entity ${entity.type.name} ${entity_color_mapping[entity.type.name]} text-light p-1 rounded'>${entity.name}</span>`);
                }
            }
            setContent(data);
        }, error => console.log("Error: " + error)
        )
    }

    // filter useeffect
    React.useEffect(() => {
        if (content && entity_types && entity_types.length > 0) {
            // query all elements with class name 'entity'
            let entities = document.getElementsByClassName('entity');
            for (let i = 0; i < entities.length; i++) {
                let entity = entities[i] as HTMLElement;
                // get classes
                let classes = entity.className.split(' ');
                let entity_type = classes[1];
                
                if (!filter.entity_types.includes(entity_type)) {
                    entity.style.display = 'none';
                } else {
                    entity.style.display = 'inline';
                }
                

            }

        }
    }, [filter]);



    /* Return a filter options for both categories and entity_types. */
    /* Options should be toggling buttons for enabling/disabling certail filter.  */
    /* Multiple categories/entities can be selected at once. */
    return (
        <>
            <Container id="filters-tab" className="bg-none text-light" >
                <Row>
                    <Col>
                        <Form.Label className="pt-3">Categories</Form.Label>
                        <Stack direction="horizontal" gap={3}>
                            {categories && categories.map((name) => (    
                                <FilterButton key={name} name={name} selected={filter.categories.includes(name)} onClick={(name) => {
                                    if (filter.categories.includes(name)) {
                                        setFilter({...filter, categories: filter.categories.filter((cat) => cat !== name)});
                                    } else {
                                        setFilter({...filter, categories: [...filter.categories, name]});
                                    }
                                }} />
                            ))}
                        </Stack>
                    </Col>
                    <Col>
                        <Form.Label className="pt-3">Entity Types</Form.Label>
                        <Stack direction="horizontal" gap={3}>
                            {entity_types && entity_types.map((name) => (    
                                <FilterButton key={name} name={name} selected={filter.entity_types.includes(name)} onClick={(name) => {
                                    if (filter.entity_types.includes(name)) {
                                        setFilter({...filter, entity_types: filter.entity_types.filter((ent) => ent !== name)});
                                    } else {
                                        setFilter({...filter, entity_types: [...filter.entity_types, name]});
                                    }
                                }} />
                            ))}
                        </Stack>
                    </Col>
                </Row>
                {/* Numerical value for setting threshold of category */}
                <Row>
                    <Col>
                        <Form.Label className="pt-3">Category Threshold</Form.Label>
                        <Form.Control type="number" value={filter.cat_threshold} min='0' max='1' step='0.01' onChange={(e) => {
                            setFilter({...filter, cat_threshold: parseFloat(e.target.value)});
                        }} />
                    </Col>
                    <Col>
                        <Form.Label className="pt-3">Entity Threshold</Form.Label>
                        <Form.Control type="number" value={filter.ent_threshold} min='0' max='1' step='0.01'onChange={(e) => {
                            setFilter({...filter, ent_threshold: parseFloat(e.target.value)});
                        }} />
                    </Col>
                </Row>
                {/* Text input for filtering by entity value */}
                {/* <Row>
                    <Col>
                        <Form.Label className="pt-3">Entity Values</Form.Label>
                        <Form.Control type="text" value={filter.entity_values} onChange={(e) => {
                            setFilter({...filter, entity_values: [e.target.value]});
                        }} />
                    </Col>
                </Row> */}
                {/* Text input for filtering by file name */}
                {/* <Row>
                    <Col>
                        <Form.Label className="pt-3">File Names</Form.Label>
                        <Form.Control type="text" value={filter.file_names} onChange={(e) => {
                            setFilter({...filter, file_names: [e.target.value]});
                        }} />
                    </Col>
                </Row> */}
                {/* Text input for filtering by file path */}
                {/* <Row>
                    <Col>
                        <Form.Label className="pt-3">File Paths</Form.Label>
                        <Form.Control type="text" value={filter.file_paths} onChange={(e) => {
                            setFilter({...filter, file_paths: [e.target.value]});
                        }} />
                    </Col>
                </Row> */}

                {/* Button for retrieving data from the database */}
                <Row>
                    <Col>
                        <Button className="mt-3" variant="primary" onClick={() => {
                            console.log(filter);
                            request_content();
                        }}>Request Data</Button>
                    </Col>
                </Row>
            </Container>
            <Container id="data-tab" className="bg-none text-light">
                {
                    content &&
                    content.map((item) => {
                        return (
                            <Container className='text-light mb-3 mt-3'>
                                {/*an empty separator line*/}
                                <div className='border rounded text-light mb-5'></div>
                                {/* filename */}
                                <Container className='text-light mb-3'> <h3>Path to file:</h3><div className='text-light mt-3'/>{item.file}</Container>
                                <Container className='text-light mb-3'> <h3 className='mb-3'>Categories:</h3> {
                                Object.keys(item.categories).map((key) => {
                                    var score = item.categories[key];
                                    if (score < filter.cat_threshold) {
                                        return;
                                    }
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
                                </Container>
                                <Container className='text-light mb-5'> <h3>Text with Named Entities:</h3><div className='text-light mt-3' dangerouslySetInnerHTML={{__html: item.text}} /></Container>
                            </Container>

                            )
                        }
                    )
                }
            </Container>
                        
        </>
    );
}

export default DataViewer;

function FilterButton (props: {name: string, selected: boolean, onClick: (name: string) => void}) {
    return (
        <Button variant={props.selected ? "primary" : "outline-primary"} onClick={() => props.onClick(props.name)}>
            {props.name}
        </Button>
    );
}