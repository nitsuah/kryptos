import { expect, test, type Page } from "@playwright/test";

// Every /api call is stubbed with page.route(), so these journeys never need the
// FastAPI backend and never depend on live data. Shapes follow src/api.ts.

const MODULES = [
  { id: "k4", title: "K4" },
  { id: "ledger", title: "Ledger" },
  { id: "attacks", title: "Attacks" },
  { id: "lab", title: "Lab" },
  { id: "system", title: "System" },
] as const;

const LEDGER = {
  counts: { eliminated: 3, statistical: 2, sampled_null: 1, open: 4 },
  entries: [],
  latest_run: null,
};

/** Healthy API: status, ledger, jobs and frontier answer; anything else is a 404. */
async function stubApi(page: Page): Promise<void> {
  await page.route("**/api/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/api/status") {
      return route.fulfill({ json: { db_enabled: true, table_counts: {}, latest_run: null } });
    }
    if (path === "/api/k4/ledger") return route.fulfill({ json: LEDGER });
    if (path === "/api/k4/attacks/jobs") return route.fulfill({ json: { jobs: [] } });
    if (path === "/api/k4/attacks/frontier") return route.fulfill({ json: { vectors: [] } });
    return route.fulfill({ status: 404, json: { detail: "not stubbed" } });
  });
}

/** Unreachable API: every call fails the way a refused connection does. */
async function stubApiDown(page: Page): Promise<void> {
  await page.route("**/api/**", (route) => route.abort("connectionrefused"));
}

function trackPageErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  return errors;
}

const activeModule = (page: Page) => page.locator("section.face.is-active");

test.describe("K4 grid", () => {
  test("renders 97 cell buttons and labels the 24 known-plaintext cells", async ({ page }) => {
    const errors = trackPageErrors(page);
    await stubApi(page);
    await page.goto("/#k4");

    const cells = page.locator("ul.cm-grid button.cm-cell");
    await expect(cells).toHaveCount(97);
    // Only crib cells carry a plaintext letter in their accessible name.
    await expect(page.locator('ul.cm-grid button[aria-label*="plaintext"]')).toHaveCount(24);
    await expect(page.locator("ul.cm-grid button.cm-cell.crib")).toHaveCount(24);

    // One labelled example per crib family.
    await expect(cells.nth(21)).toHaveAttribute("aria-label", /^position 21: \w, plaintext E \(EAST\)$/);
    await expect(cells.nth(63)).toHaveAttribute("aria-label", /plaintext B \(BERLIN\)$/);
    await expect(cells.nth(0)).not.toHaveAttribute("aria-label", /plaintext/);
    expect(errors).toEqual([]);
  });

  test("focusing a crib cell reads out its position and plaintext letter", async ({ page }) => {
    await stubApi(page);
    await page.goto("/#k4");
    await page.locator("ul.cm-grid button.cm-cell").nth(69).focus();
    const readout = page.locator(".cm-readout");
    await expect(readout).toContainText("POS 69");
    await expect(readout).toContainText("CLOCK");
  });
});

test.describe("module deep links", () => {
  for (const [i, m] of MODULES.entries()) {
    test(`#${m.id} opens the ${m.title} module`, async ({ page }) => {
      await stubApi(page);
      await page.goto(`/#${m.id}`);
      await expect(activeModule(page)).toHaveAttribute("aria-label", `${m.title}, ${i + 1} of ${MODULES.length}`);
      await expect(page).toHaveTitle(`${m.title} · KRYPTOS`);
      await expect(page.locator(".dock-btn[aria-current='true'] .dock-title")).toHaveText(m.title);
    });
  }

  test("the next arrow walks every module in order, updates the hash and wraps around", async ({ page }) => {
    await stubApi(page);
    await page.goto("/#k4");
    await expect(activeModule(page)).toHaveAttribute("aria-label", /^K4, 1 of 5$/);

    for (const m of MODULES.slice(1)) {
      await page.getByRole("button", { name: "Next module" }).click();
      await expect(page).toHaveURL(new RegExp(`#${m.id}$`));
      await expect(page).toHaveTitle(`${m.title} · KRYPTOS`);
    }
    await page.getByRole("button", { name: "Next module" }).click();
    await expect(page).toHaveURL(/#k4$/);
    await expect(activeModule(page)).toHaveAttribute("aria-label", /^K4, 1 of 5$/);
  });

  test("legacy hashes still land on the right module", async ({ page }) => {
    await stubApi(page);
    await page.goto("/#vault");
    await expect(activeModule(page)).toHaveAttribute("aria-label", /^Lab, 4 of 5$/);
  });
});

test.describe("API availability", () => {
  test("a healthy API shows ONLINE", async ({ page }) => {
    await stubApi(page);
    await page.goto("/#k4");
    await expect(page.getByRole("img", { name: "API online" })).toBeVisible();
    await expect(page.getByText("The API is not answering")).toHaveCount(0);
  });

  test("an unreachable API shows the unreachable state, not stale ONLINE", async ({ page }) => {
    const errors = trackPageErrors(page);
    await stubApiDown(page);
    await page.goto("/#k4");

    await expect(page.getByRole("img", { name: "API offline" })).toBeVisible();
    await expect(page.getByRole("img", { name: "API online" })).toHaveCount(0);
    await expect(page.getByText("The API is not answering")).toBeVisible();
    // The static cipher grid is still usable without the API.
    await expect(page.locator("ul.cm-grid button.cm-cell")).toHaveCount(97);
    expect(errors).toEqual([]);
  });

  test("a 503 from the API is also treated as unreachable", async ({ page }) => {
    await page.route("**/api/**", (route) => route.fulfill({ status: 503, body: "upstream down" }));
    await page.goto("/#system");
    await expect(page.getByRole("img", { name: "API offline" })).toBeVisible();
  });
});
