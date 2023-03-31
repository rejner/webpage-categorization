

export interface Content {
    'categories': { [key: string]: number };
    'entities': Entity[],
    'text': string,
    'file': string | undefined,
    'id': number,
}

export interface Entity {
    'id': number,
    'name': string,
    'type': EntityType,
}

export interface EntityType {
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

export interface File_v2 {
    'id': number,
    'name': string,
    'path': string,
}

export interface Message_v2 {
    'id': number,
    'text': string,
    'categories': Category_v2[],
    'entities': Entity[],
}

export interface Category_v2 {
    'id': number,
    'message_id': number,
    'category_id': number,
    'confidence': number,
    'category': {
        'id': number,
        'name': string,
    }
}

export interface Content_v2 {
    'id': number,
    'file': File_v2,
    'hash': string,
    'header': string,
    'author': string,
    'messages': Message_v2[],
    'merged_text': string,
    'merged_categories': { [key: string]: number },
}