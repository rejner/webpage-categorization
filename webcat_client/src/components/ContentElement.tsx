import React, { useEffect, useMemo } from 'react';
import { Content, NamedEntity, entity_color_mapping } from '../models/Content';
import { Stack, Container, Button, Form, Row, Col, Spinner } from 'react-bootstrap';
import { AppContext } from '../index';
import { WebCatFilters } from './DataViewer';


interface ContentElementProps {
    content: Content,
    filter?:  WebCatFilters,
    onDelete?: (id: number) => void, 
}

const LONG_TEXTUAL_CONTENT = ['post-message']

export const ContentElement = (props: ContentElementProps) => {
    const [content, setContent] = React.useState<Content>();
    // long textual content might be split into multiple attributes
    const [mergedText, setMergedText] = React.useState('');
    const [mergedCategories, setMergedCategories] = React.useState<any>({});

    useEffect(() => {
        setContent(props.content);
    }, [props.content]);

    useEffect (() => {
        if (content !== undefined) {
            processContent();
        }
    }, [content]);

    useEffect(() => {
    }, [mergedText, mergedCategories]);

    function processContent() {
        let merged_text = "";
        let merged_categories: { [key: string]: number } = {};
        for (let a of content!.attributes) {
            if (a.entities !== null && a.entities.length > 0) {
                a.content = insertNamedEntitiesIntoText(a.content, a.entities);
            }
            //console.log(a.categories);
            if (LONG_TEXTUAL_CONTENT.includes(a.type.tag)) {
                merged_text += `[CHUNK #${a.tag}] ` + a.content + " ";
                //console.log(a.categories);
                for (let cat of a.categories) {
                    let key = cat.category.name;
                    if (key in merged_categories) {
                        merged_categories[key] = Math.max(merged_categories[key], cat.score);
                    } else {
                        merged_categories[key] = cat.score;
                    }
                }
                //console.log(merged_categories);
            }
        }
        if (merged_text.length > 0) {
            setMergedText(merged_text);
        }
        if (Object.keys(merged_categories).length > 0) {
            setMergedCategories(merged_categories);
        }
    }

    function insertNamedEntitiesIntoText(text: string, entities: NamedEntity[]) {
        for (let e of entities) {
            let color = entity_color_mapping[e.type.name];
            text = text.replace(e.name, `<span class='${color} text-light p-1 rounded'>${e.name}</span>`);
        }
        return text;
    }

    return <>
        { content !== undefined &&
        <Container className='text-light mb-3 mt-3'>
            {/*an empty separator line*/}
            <div className='border rounded text-light mb-5'></div>
            {/* filename */}
            
            {
                props.onDelete !== undefined &&
                <Container className='text-light mb-3'> 
                    <Row>
                        <ExpandableText text={content!.file.path} className='text-light ml-3' />   
                        {/* Delete button, column only of button size pushing it most to the right */}
                        <Col xs='auto'>
                            <Button className="mt-3" variant="danger" onClick={() => {
                                {
                                    if (!window.confirm('Are you sure you wish to delete this item?')) return;
                                    if (props.onDelete !== undefined) props.onDelete(content!.id);
                                }
                            }}>Delete</Button>
                        </Col>
                    </Row>
                </Container>
            }
  
            
            <Container className='text-light mb-3'> <h3 className='mb-3'>Categories:</h3> {
            Object.keys(mergedCategories).map((key) => {
                var score = mergedCategories[key];
                if (props.filter && score < props.filter.cat_threshold) {
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
                <Row className={className} style={{backgroundColor: color}} key={key}> 
                    <Col>{key}</Col>
                    <Col>{score.toFixed(2)}</Col>
                </Row>
                );
            }
            
            )}
            </Container>
            {
            content!.attributes.map((item, index) => {
                // skip long textual content if it is not the first chunk (all chunks are merged into one)
                if (LONG_TEXTUAL_CONTENT.includes(item.type.tag) && item.tag != '0') {
                    return;
                }
                return (
                    <Container className='text-light mb-3' key={index}>
                        <h3 className='mb-3'>{item.type.name}</h3>
                        <div className='text-light mt-3' dangerouslySetInnerHTML={{__html: LONG_TEXTUAL_CONTENT.includes(item.type.tag) && item.tag == '0' ? mergedText : item.content}} />
                    </Container>
                );

            })
            }
        </Container>
        }
        </>
    
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