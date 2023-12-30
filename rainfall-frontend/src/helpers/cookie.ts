export async function getCsrf(): Promise<string> {
  await fetch('/api/v1/csrf');
  return (
    document.cookie
      .split('; ')
      .find((row) => row.startsWith('_csrf_token='))
      ?.split('=')[1] || ''
  );
}
