

export interface Element {
    'id': number;
    'tag': string;
    'parent_tag': string;
    'grandparent_tag': string;
    'depth': number;
    'xPath': string;
    'classes': string;
    'type': ElementType;
}

export interface ElementType {
    'id': number;
    'name': string;
    'tag': string;
    'analysis_flag': boolean;
}
