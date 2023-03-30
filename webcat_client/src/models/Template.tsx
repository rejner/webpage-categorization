import { Element, Element_v2 } from './Element';

export interface Template {
    'id': number;
    'creation_date': string;
    'origin_file': string;
    'elements': Element[];
}

export interface Template_v2 {
    'id': number;
    'creation_date': string;
    'origin_file': string;
    'elements': Element_v2[];
}