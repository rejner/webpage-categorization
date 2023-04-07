

export interface NamedEntity {
    'id': number,
    'name': string,
    'type': NamedEntityType,
}

export interface NamedEntityType {
    'id': number,
    'name': string,
    'tag': string | null,
}

export const entity_color_mapping: any = {
    "product": 'bg-primary',
    "person": 'bg-success',
    "location": 'bg-warning',
    "event": 'bg-info',
    "group": 'bg-secondary',
    "corporation": 'bg-danger',
    "creative_work": 'bg-dark',
}

export interface File {
    'id': number,
    'name': string,
    'path': string,
}

export interface Attribute {
    'id': number,
    'content': string,
    'tag': string,
    'type': AttributeType,
    'type_id': number,
    'categories': Category[],
    'entities': NamedEntity[],
}

export interface AttributeType {
    'id': number,
    'name': string,
    'tag': string,
}

export interface Category {
    'id': number,
    'message_id': number,
    'category_id': number,
    'score': number,
    'category': {
        'id': number,
        'name': string,
    }
}

export interface Content {
    'id': number,
    'file': File,
    'hash': string,
    'attributes': Attribute[],
    // 'merged_text': string,
    // 'merged_categories': { [key: string]: number },
}

export interface InteractiveContent {
    'text': string,
    'entities': NamedEntity[],
    'categories': Category[],
}