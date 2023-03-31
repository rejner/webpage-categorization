

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

export interface Content_v2 {
    'categories': { [key: string]: number }[];
    'entities': [Entity[]],
    'message': string[],
    'file_path': string,
    'id': number,
    'hash': string,
    'header': string,
    'author': string,
    'merged_text': string,
    'merged_categories': { [key: string]: number },
}