import { type Integration } from './integration';

export declare interface User {
  id: string;
  name: string;
  email: string;
  picture_url: string;
  is_welcomed: boolean;
  integration: Integration;
}
