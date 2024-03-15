import { type File } from './file';

export declare interface Release {
  id: string;
  name: string;
  description: string;
  site_id: string;
  files: File[];
}
