import { type Release } from './release';

export declare interface Site {
  id: string;
  name: string;
  releases: Release[];
  netlify_site_id: string;
  netlify_url: string;
}
