import { type Release } from './release';

export declare interface Site {
  id: string;
  name: string;
  releases: Release[];
}
