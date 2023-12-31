export function getCsrf(): string {
  return (
    document.cookie
      .split('; ')
      .find((row) => row.startsWith('_csrf_token='))
      ?.split('=')[1] || ''
  );
}
