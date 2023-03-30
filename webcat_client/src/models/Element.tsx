
export interface Element {
    'id': number;
    'tag': string;
    'classes': string[];
    'id_attr': string;
    'type': string;
}

export interface Element_v2 {
    'id': number;
    'tag': string;
    'parent_tag': string;
    'grandparent_tag': string;
    'depth': number;
    'type': string;
}