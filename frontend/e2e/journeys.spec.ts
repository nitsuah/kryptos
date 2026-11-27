import { expect, test, type Page } from "@playwright/test";
import { k3Stages, SECTION_DATA } from "../src/cipher";

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
// The first-visit card would sit over the dashboard.
// The first-visit tests skip this, so only one script ever touches the flag.
test.beforeEach(async ({ page }, testInfo) => {
  if (testInfo.titlePath.includes("first visit")) return;
  await page.addInitScript(() => localStorage.setItem("kryptos-welcome-seen", "1"));
});

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

test("visitor K3 decrypt panel displays the length validation error", async ({ page }) => {
  await stubApi(page);
  await page.goto("http://visitor.localhost:4173/#lab");
  const decryptForm = page
    .locator("form")
    .filter({
      has: page.locator('textarea[placeholder^="EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ"]'),
    });
  await decryptForm.locator("select").selectOption("K3");
  await decryptForm.locator("textarea").fill("A");
  await decryptForm.getByRole("button", { name: "Execute" }).click();
  await expect(decryptForm.locator(".result.error")).toContainText(
    "K3 ciphertext must be 336 chars (got 1)",
  );
});

test("unauthenticated localhost uses browser K1-K3 while keeping K4 server-backed", async ({ page }) => {
  await stubApi(page);
  let decryptRequests = 0;
  await page.route("**/api/decrypt", async (route) => {
    decryptRequests += 1;
    await route.fulfill({ status: 401, body: "operator token required" });
  });
  await page.goto("http://localhost:4173/#lab");

  const decryptForm = page
    .locator("form")
    .filter({
      has: page.locator('textarea[placeholder^="EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ"]'),
    });
  await decryptForm.locator("select").selectOption("K3");
  await decryptForm.locator("textarea").fill("A");
  await decryptForm.getByRole("button", { name: "Execute" }).click();
  await expect(decryptForm.locator(".result.error")).toContainText(
    "K3 ciphertext must be 336 chars (got 1)",
  );
  expect(decryptRequests).toBe(0);

  await decryptForm.locator("select").selectOption("K4");
  await decryptForm.locator("textarea").fill("unsolved ciphertext");
  await decryptForm.getByRole("button", { name: "Execute" }).click();
  await expect.poll(() => decryptRequests).toBe(1);
  await expect(decryptForm.locator(".result.error")).toContainText("[401]");
});

test("K3 stage builder rejects incomplete ciphertext before grid padding", () => {
  expect(() => k3Stages("A")).toThrow(/K3 ciphertext must be 336 chars/);
  expect(k3Stages(SECTION_DATA.K3.cipher)).toHaveLength(4);
});

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
    await page.clock.install();
    await page.goto("/#k4");

    // Inside the wake window there is one calm state and no error wording.
    await expect(page.getByRole("img", { name: "API waking" })).toBeVisible();
    await page.clock.fastForward(4_000);
    await expect(page.getByRole("status").filter({ hasText: "Waking the server" })).toBeVisible();
    await expect(page.getByText("The API is not answering")).toHaveCount(0);
    // The banner pushes the header down without stretching it or the stage.
    const banner = (await page.locator(".coldstart-banner").boundingBox())!;
    const hud = (await page.locator(".hud").boundingBox())!;
    const stage = (await page.locator(".stage").boundingBox())!;
    expect(hud.y).toBeGreaterThanOrEqual(banner.y + banner.height - 1);
    expect(hud.height).toBeLessThan(120);
    expect(stage.height).toBeGreaterThan(300);
    await page.clock.fastForward(90_000);

    await expect(page.getByRole("img", { name: "API offline" })).toBeVisible();
    await expect(page.getByRole("img", { name: "API online" })).toHaveCount(0);
    await expect(page.getByText("The API is not answering")).toBeVisible();
    // The static cipher grid is still usable without the API.
    await expect(page.locator("ul.cm-grid button.cm-cell")).toHaveCount(97);
    expect(errors).toEqual([]);
  });

  test("System and Ledger defer API errors during the wake window", async ({ page }) => {
    await stubApiDown(page);
    await page.clock.install();
    await page.goto("/#system");

    const connection = page.locator(".sys-conn");
    await expect(connection.getByText("waking")).toBeVisible();
    await expect(connection.getByText(/\/api\/status failed/)).toHaveCount(0);

    await page.evaluate(() => {
      window.location.hash = "#ledger";
    });
    await expect(page.getByText("Loading ledger…")).toBeVisible();
    await expect(page.getByText(/Ledger unavailable/)).toHaveCount(0);

    await page.clock.fastForward(90_000);
    await expect(page.getByText(/Ledger unavailable/)).toBeVisible();

    await page.evaluate(() => {
      window.location.hash = "#system";
    });
    await expect(connection.getByText("unreachable")).toBeVisible();
    await expect(connection.getByText(/\/api\/status failed/)).toBeVisible();
  });

  test("a 503 from the API is also treated as unreachable", async ({ page }) => {
    await page.route("**/api/**", (route) => route.fulfill({ status: 503, body: "upstream down" }));
    await page.clock.install();
    await page.goto("/#system");
    await expect(page.getByRole("img", { name: "API waking" })).toBeVisible();
    await page.clock.fastForward(91_000);
    await expect(page.getByRole("img", { name: "API offline" })).toBeVisible();
  });
});

const VECTOR = {
  id: "p1",
  priority: 1,
  name: "P1 — Example vector",
  status: "untested",
  description: "An example.",
  layer_count: 1,
  combo_estimate: null,
  runnable: true,
};

test.describe("visitors", () => {
  // Any host that is not local counts as a visitor's view.
  const VISITOR = "http://visitor.localhost:4173";

  test("operator routes are not called and the controls say why", async ({ page }) => {
    await stubApi(page);
    await page.route("**/api/k4/attacks/frontier", (r) => r.fulfill({ json: { vectors: [VECTOR] } }));
    const called: string[] = [];
    page.on("request", (r) => called.push(new URL(r.url()).pathname));
    await page.goto(`${VISITOR}/#attacks`);
    await expect(page.getByText("Read-only view")).toBeVisible();
    await expect(page.getByRole("button", { name: /Run Attack/ })).toBeDisabled();
    expect(called.filter((p) => p.startsWith("/api/k4/attacks/jobs"))).toEqual([]);

    await page.getByRole("searchbox", { name: "Search attacks" }).fill("zzzz");
    await expect(page.getByText("No attacks match.")).toBeVisible();
    await page.getByRole("button", { name: "clear search" }).click();
    await expect(page.getByRole("button", { name: /Example vector/ })).toBeVisible();
  });

  test("solved sections decrypt in the browser", async ({ page }) => {
    await stubApi(page);
    const called: string[] = [];
    page.on("request", (r) => called.push(new URL(r.url()).pathname));
    await page.goto(`${VISITOR}/#lab`);
    await expect(page.getByRole("button", { name: "Verify vs backend" })).toBeDisabled();
    await page.getByPlaceholder("PALIMPSEST").fill("PALIMPSEST");
    await page.locator("textarea").fill("EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ");
    await page.getByRole("button", { name: "Execute" }).click();
    await expect(page.locator(".lab-tools .result.plaintext")).toHaveText("BETWEENSUBTLESHADINGANDTHEABSENC");
    expect(called).not.toContain("/api/decrypt");

    await page.locator(".lab-tools select").selectOption("K3");
    await page.locator("textarea").fill("A");
    await page.getByRole("button", { name: "Execute" }).click();
    await expect(page.locator(".lab-tools .result.error")).toContainText("must be 336 chars");
  });
});

test("log failures show a cause-neutral message and Retry opens a new stream", async ({ page }) => {
  await stubApi(page);
  await page.addInitScript(() => {
    localStorage.removeItem("kryptos.apiToken");
    localStorage.setItem("kryptos.logToken", "test-log-token");
    class FailingEventSource {
      static CLOSED = 2;
      static instances = 0;
      readyState = 0;
      onerror: ((event: Event) => void) | null = null;
      onmessage: ((event: MessageEvent) => void) | null = null;
      onopen: ((event: Event) => void) | null = null;
      constructor() {
        FailingEventSource.instances += 1;
        setTimeout(() => this.onerror?.(new Event("error")), 0);
        setTimeout(() => this.onerror?.(new Event("error")), 1);
        setTimeout(() => this.onerror?.(new Event("error")), 2);
      }
      addEventListener() {}
      close() {
        this.readyState = FailingEventSource.CLOSED;
      }
    }
    Object.defineProperty(window, "EventSource", {
      configurable: true,
      value: FailingEventSource,
    });
  });

  await page.goto(`http://visitor.localhost:4173/#system`);
  await expect(page.getByText("Live log unavailable. Check the server connection and retry.")).toBeVisible();
  await expect(page.getByText("The live log is not open to visitors on this server.")).toHaveCount(0);
  const initialAttempts = await page.evaluate(() => (window.EventSource as any).instances);
  expect(initialAttempts).toBeGreaterThan(0);
  await page.getByRole("button", { name: "Retry" }).click();
  await expect
    .poll(() => page.evaluate(() => (window.EventSource as any).instances))
    .toBe(initialAttempts + 1);
});

test.describe("first visit", () => {
  test("the card explains Kryptos, closes with Esc and reopens from ?", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await stubApi(page);
    await page.goto("/#k4");
    const card = page.getByRole("dialog", { name: "What is Kryptos?" });
    await expect(card).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(card).toHaveCount(0);
    await page.getByRole("button", { name: "What is Kryptos?" }).click();
    await card.getByRole("button", { name: "Watch K1 decode" }).click();
    await expect(page).toHaveURL(/#lab$/);
    await expect(page.locator(".dock-btn .dock-title").first()).toBeVisible();
    for (const box of await page.locator(".dock-btn").all()) {
      const size = await box.boundingBox();
      expect(size!.height).toBeGreaterThanOrEqual(44);
      expect(size!.width).toBeGreaterThanOrEqual(44);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
  });
});

test.describe("status key", () => {
  for (const hash of ["k4", "ledger"]) {
    test(`on #${hash} it opens from the keyboard and defines every term`, async ({ page }) => {
      await stubApi(page);
      await page.goto(`/#${hash}`);
      const key = page.locator("section.face.is-active details.status-key");
      await expect(key.locator("dl")).toBeHidden();
      await key.locator("summary").press("Enter");
      await expect(key.locator("dt")).toHaveText([
        "Eliminated",
        "Statistical",
        "Sampled null",
        "Open",
        "Null",
        "Crib",
      ]);
      for (const definition of await key.locator("dd").all()) {
        await expect(definition).toBeVisible();
        await expect(definition).not.toBeEmpty();
      }
      await key.locator("summary").click();
      await expect(key.locator("dl")).toBeHidden();
    });
  }
});
