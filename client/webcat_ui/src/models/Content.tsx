

export interface Content {
    'categories': { [key: string]: number };
    'entities': Entity[],
    'text': string,
    'file': string | undefined
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
}