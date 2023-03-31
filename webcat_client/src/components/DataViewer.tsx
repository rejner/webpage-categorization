import React from 'react';
import { Stack, Container, Button, Form, Row, Col, Spinner } from 'react-bootstrap';
import { AppContext } from '../index';
import {Content, Content_v2, Entity, entity_color_mapping} from '../models/Content';

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
    const [content, setContent] = React.useState() as [Content_v2[], (content: Content_v2[]) => void];
    const [isLoading , setIsLoading] = React.useState(false);
    const [filter, setFilter] = React.useState<WebCatFilters>({
        categories: ['all'],
        cat_threshold: 0.0,
        entity_types: ['all'],
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
            let cats = ['all'] as string[];
            cats.push(...info.categories);
            let ents = ['all'] as string[];
            ents.push(...info.entity_types);
            setCategories(cats);
            setEntityTypes(ents);
            
        }, error => console.log("Error: " + error)
        )
    }, []);

    function request_content() {
        setIsLoading(true);
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
            let contents: Content_v2[] = data;
            for (let c of contents) {
                let merged_text = "";
                let merged_entities: Entity[] = [];
                let merged_categories: { [key: string]: number } = {};
                for (let m of c.messages) {
                    merged_text += m.text + " ";
                    merged_entities = merged_entities.concat(m.entities);
                    for (let cat of m.categories) {
                        let key = cat.category.name;
                        if (key in merged_categories) {
                            merged_categories[key] = Math.max(merged_categories[key], cat.confidence);
                        } else {
                            merged_categories[key] = cat.confidence;
                        }
                    }
                }

                for (let entity of merged_entities) {
                    // replace entity with <span> tag
                    merged_text = merged_text.replace(entity.name, `<span class='${entity_color_mapping[entity.type.name]} text-light p-1 rounded'>${entity.name}</span>`);
                }
                // merge categories by taking the maximum of each category
                console.log(merged_categories);
                c.merged_categories = merged_categories;
                c.merged_text = merged_text;
            
            }
            setContent(data);
        }, error => console.log("Error: " + error)
        )
        .finally(() => setIsLoading(false));
    }

    // filter useeffect
    React.useEffect(() => {
        if (content && filter.entity_types && filter.entity_types.length > 0) {
            // query all elements with class name 'entity'
            let entities = document.getElementsByClassName('entity');
            for (let i = 0; i < entities.length; i++) {
                let entity = entities[i] as HTMLElement;
                // get classes
                let classes = entity.className.split(' ');
                let entity_type = classes[1];
                
                if (!filter.entity_types.includes(entity_type) && !filter.entity_types.includes('all')) {
                    // mute the entity but keep visible
                    entity.style.opacity = '0.2';
                    // set alpha of background color to 0
                    
                } else {
                    // entity.style.display = 'inline';
                    entity.style.opacity = '1';

                }
                
            }

        }
    }, [filter]);

    function delete_content(id: number) {
        fetch(`http://${server_ip}:${server_port}${server_api}/webcat_data_provider`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({id: id})
        })
        .then(response => response.json(), error => console.log("Error: " + error))
        .then(data => {
            console.log('Success:', data);
            if (data.error) {
                alert(data.error)
                return;
            }
            request_content();
        }, error => console.log("Error: " + error)
        )
    }



    /* Return a filter options for both categories and entity_types. */
    /* Options should be toggling buttons for enabling/disabling certail filter.  */
    /* Multiple categories/entities can be selected at once. */
    return (
        <>
            <Container id="filters-tab" className="bg-none text-light" >
                {/* Row with elements with wrap property, horizontal, stack left */}
                <Row className="flex-wrap justify-content-md-start">
                    <Form.Label className="pt-3">Categories</Form.Label>
                    {categories && categories.map((name) => (
                        <Col key={name} md="auto" className="p-1">    
                                <FilterButton key={name} name={name} selected={filter.categories.includes(name)} onClick={(name) => {
                                    if (filter.categories.includes(name)) {
                                        setFilter({...filter, categories: filter.categories.filter((cat) => cat !== name)});
                                    } else {
                                        setFilter({...filter, categories: [...filter.categories, name]});
                                    }
                                }} />
                                </Col>
                        ))}
                </Row>
                <Row className="flex-wrap justify-content-md-start">
                    <Form.Label className="pt-3">Entity Types</Form.Label>
                        {entity_types && entity_types.map((name) => (
                            <Col key={name} md="auto" className="p-1">      
                            <FilterButton key={name} name={name} selected={filter.entity_types.includes(name)} onClick={(name) => {
                                if (filter.entity_types.includes(name)) {
                                    setFilter({...filter, entity_types: filter.entity_types.filter((ent) => ent !== name)});
                                } else {
                                    setFilter({...filter, entity_types: [...filter.entity_types, name]});
                                }
                            }} />
                            </Col>
                        ))}
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
                    {isLoading &&
                        <Col>
                            <Spinner animation="border" role="status" className='mt-3'>
                            </Spinner>
                        </Col>
                    }
                </Row>
            </Container>
            {/* Show length of content */}
            {
                content &&
                <Container id="data-tab" className="bg-none text-light">
                    <Row>
                        <Col>
                            <h4>Number of results: {content.length}</h4>
                        </Col>
                    </Row>
                </Container>
            }
            <Container id="data-tab" className="bg-none text-light">
                {
                    content &&
                    content.map((item) => {
                        return (
                            <Container className='text-light mb-3 mt-3'>
                                {/*an empty separator line*/}
                                <div className='border rounded text-light mb-5'></div>
                                {/* filename */}
                                
                                <Container className='text-light mb-3'> 
                                    <Row>
                                        <ExpandableText text={item.file.path} className='text-light ml-3' />   
                                        {/* Delete button, column only of button size pushing it most to the right */}
                                        <Col xs='auto'>
                                            <Button className="mt-3" variant="danger" onClick={() => {
                                                delete_content(item.id);
                                            }}>Delete</Button>
                                        </Col>
                                    </Row>
                                </Container>
                                
                                <Container className='text-light mb-3'> <h3 className='mb-3'>Categories:</h3> {
                                Object.keys(item.merged_categories).map((key) => {
                                    var score = item.merged_categories[key];
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
                                <Container className='text-light mb-3'> <h3 className='mb-3'>Header:</h3> <div className='text-light mt-3' dangerouslySetInnerHTML={{__html: item.header}} /></Container>
                                <Container className='text-light mb-3'> <h3 className='mb-3'>Author:</h3> <div className='text-light mt-3' dangerouslySetInnerHTML={{__html: item.author}} /></Container>
                                <Container className='text-light mb-5'> <h3>Text with Named Entities:</h3><div className='text-light mt-3' dangerouslySetInnerHTML={{__html: item.merged_text}} /></Container>
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

function ExpandableText (props: {text: string, className: string}) {
    /* Display plus and minus icon */
    const [expanded, setExpanded] = React.useState(false);
    return (
        <Col className={props.className}>
            {/* Display plus icon which will expand the file path if needed */}
            <Button variant="outline-primary" onClick={() => setExpanded(!expanded)}>
                {expanded ? 'hide' : 'show more'}
            </Button>
            {/* Display file path if expanded */}
            {expanded && 
            <>
                <Container className='text-light mb-3 mt-3'> <h4>Path to file:</h4></Container>
                <Container className='text-light mb-3'> <h6>{props.text}</h6></Container>
            </>
            }
        </Col>
    );
}