// Cloudflare Pages Function for same-origin /api/* requests.
// The dashboard calls the Render API directly (VITE_API_BASE_URL). If that
// build variable is ever missing, relative /api calls land here; answer with
// JSON that says what is wrong instead of the SPA's index.html.
export function onRequest({ request }) {
  const { pathname } = new URL(request.url);
  return new Response(
    JSON.stringify({
      error: `API base URL is not configured for this build (set VITE_API_BASE_URL); no handler for ${pathname}.`,
    }),
    {
      status: 404,
      headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
    },
  );
}
