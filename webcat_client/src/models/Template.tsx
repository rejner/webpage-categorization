import { Element } from './Element';

export interface Template {
    'id': number;
    'creation_date': string;
    'origin_file': string;
    'elements': Element[];
}
