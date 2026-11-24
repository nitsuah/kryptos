// Browser journeys for the dashboard against `vite preview` of the production
// build, with every /api call stubbed in the spec (no backend needed). Run in
// the pinned Playwright image (see .github/workflows/ci-fast.yml):
//   docker run --rm -v "$PWD:/w" -w /w/frontend -e CI=true \
//     mcr.microsoft.com/playwright:v1.65.1-jammy sh -c "npm ci && npm run test:e2e"
import { defineConfig, devices } from "@playwright/test";

const PORT = 4173;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "retain-on-failure",
    reducedMotion: "reduce",
    timezoneId: "UTC",
    locale: "en-US",
    viewport: { width: 1280, height: 800 },
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `npm run build && npm run preview -- --host 127.0.0.1 --port ${PORT} --strictPort`,
    url: `http://127.0.0.1:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
  },
});
