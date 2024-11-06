import { getCsrf } from './cookie';

export async function deleteSite(id: string) {
  const resp = await fetch(`/api/v1/site/${id}`, {
    method: 'DELETE',
    headers: { 'X-CSRFToken': getCsrf() },
  });
  if (!resp.ok) {
    if (resp.headers.get('Content-Type') == 'application/json') {
      const data = await resp.json();
      return data.error;
    } else {
      return 'An unknown error occurred';
    }
    return '';
  }
}
