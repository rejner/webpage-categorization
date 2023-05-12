import React from 'react';
import { Stack, Container, Button, Form, Row, Col, Spinner } from 'react-bootstrap';
import { AppContext } from '../index';
import {Content, NamedEntity, entity_color_mapping} from '../models/Content';
import {ContentElement } from './ContentElement';

export interface WebCatFilters {
    categories: string[],
    cat_threshold: number,
    entity_types: string[],
    ent_threshold: number,
    entity_values: string[],
    file_names: string[],
    file_paths: string[],
    authors: string[],
}

interface WebCatInfo {
    categories: string[],
    entity_types: string[],
}

function DataViewer() {
    const [categories, setCategories] = React.useState() as [string[], (categories: string[]) => void];
    const [entity_types, setEntityTypes] = React.useState() as [string[], (entity_types: string[]) => void];
    const [content, setContent] = React.useState() as [Content[], (content: Content[]) => void];
    const [isLoading , setIsLoading] = React.useState(false);
    const [showAdvancedFilters, setShowAdvancedFilters] = React.useState(false);
    const [filter, setFilter] = React.useState<WebCatFilters>({
        categories: ['all'],
        cat_threshold: 0.9,
        entity_types: ['all'],
        ent_threshold: 0.9,
        entity_values: [],
        file_names: [],
        file_paths: [""],
        authors: [""],
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
            let contents: Content[] = data;
            setContent(contents);
        }, error => console.log("Error: " + error)
        )
        .finally(() => setIsLoading(false));
    }

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
                <Form.Switch className="pt-3" id="custom-switch" label="Show Advanced Filters" checked={showAdvancedFilters} onChange={(e) => {
                    setShowAdvancedFilters(e.target.checked);
                }} />
                {showAdvancedFilters &&
                    <>
                    {/* Numerical value for setting threshold of category */}
                    <Row className="w-25">
                        <Col className=''>
                            <Form.Label className="pt-3">Category Threshold</Form.Label>
                            <Form.Control type="number" value={filter.cat_threshold} min='0' max='1' step='0.01' onChange={(e) => {
                                setFilter({...filter, cat_threshold: parseFloat(e.target.value)});
                            }} />
                            {/*description of threshold*/}
                            <Form.Text className="text-muted">
                                The threshold for the category confidence.
                            </Form.Text>
                        </Col>
                    </Row>
                    <Stack direction="vertical" gap={1}>
                        {/* Post author search */}
                        <Form.Label className="pt-3">Authors</Form.Label>
                        {
                            filter.authors &&
                            filter.authors.map((author, index) => (
                                <Stack direction="horizontal" gap={3} key={index}>
                                    <Form.Control key={index} type="text" placeholder="Enter author" value={author} className='w-50'
                                        onChange={(e) => {
                                        let authors = filter.authors;
                                        authors[index] = e.target.value;
                                        setFilter({...filter, authors: authors});
                                        }
                                    } />
                                    <Button variant="danger" onClick={() => {
                                        let authors = filter.authors;
                                        authors.splice(index, 1);
                                        setFilter({...filter, authors: authors});
                                    }
                                    }>Remove</Button>
                                </Stack>
                            ))
                        }
                        <Form.Text className="text-muted">
                            The authors of the posts (subwords will get matched as well).
                        </Form.Text>
                        <Button className="w-25 mt-2" variant="outline-primary" onClick={() => { 
                            setFilter({...filter, authors: [...filter.authors, '']});
                        }}>Add</Button>
                    
                    </Stack>
                    <Stack direction="vertical" gap={1}>
                        <Form.Label className="pt-3">File Path</Form.Label>
                        {
                            filter.file_paths &&
                            filter.file_paths.map((path, index) => (
                                <Stack direction="horizontal" gap={3} key={index}>
                                    <Form.Control key={index} type="text" placeholder="Enter path to the file" value={path} className='w-50'
                                        onChange={(e) => {
                                        let paths = filter.file_paths;
                                        paths[index] = e.target.value;
                                        setFilter({...filter, file_paths: paths});
                                    }
                                    } />
                                    <Button variant="danger"  onClick={() => {
                                        let paths = filter.file_paths;
                                        paths.splice(index, 1);
                                        setFilter({...filter, file_paths: paths});
                                    }}>Remove</Button>
                                </Stack>
                                
                            ))
                        }
                        <Form.Text className="text-muted">
                            The path to the file (wildcards * can be used as well).
                        </Form.Text>

                        <Button variant="outline-primary" className="w-25 mt-2" onClick={() => {
                            setFilter({...filter, file_paths: [...filter.file_paths, '']});
                        }}>Add</Button>
    
            
                
                    </Stack>
                </>
            }
            {/* Button for retrieving data from the database */}
            <Stack direction="vertical" gap={3} className='justify-content-center'>
                <Button className="mt-3 w-25" variant="primary" onClick={() => {
                    console.log(filter);
                    request_content();
                }} disabled={isLoading}>{isLoading &&
                        <Spinner animation="border" role="status" size="sm">
                        </Spinner>
                    }
                    {!isLoading &&
                        "Request Data"
                    }
                </Button>
            </Stack>
            
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
                                <ContentElement key={item.id} content={item} filter={filter} onDelete={delete_content} />
                            );
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

