import { type File } from './file';

export declare interface Release {
  id: string;
  name: string;
  site_id: string;
  files: File[];
}
