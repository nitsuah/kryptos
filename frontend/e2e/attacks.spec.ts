import { expect, test } from "@playwright/test";

const VECTOR = {
  id: "p1_crib_constraints",
  priority: 1,
  name: "P1 — Crib constraints",
  status: "untested",
  description: "A deterministic test vector.",
  layer_count: 1,
  combo_estimate: 1,
  runnable: false,
};

test("Attacks search shows a recoverable no-match state", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("kryptos-welcome-seen", "1"));
  await page.route("**/api/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/api/status") {
      return route.fulfill({ json: { db_enabled: true, table_counts: {}, latest_run: null } });
    }
    if (path === "/api/k4/ledger") {
      return route.fulfill({
        json: { counts: { eliminated: 0, statistical: 0, sampled_null: 0, open: 0 }, entries: [], latest_run: null },
      });
    }
    if (path === "/api/k4/attacks/jobs") {
      return route.fulfill({ json: { jobs: [] } });
    }
    if (path === "/api/k4/attacks/frontier") {
      return route.fulfill({ json: { vectors: [VECTOR] } });
    }
    return route.fulfill({ status: 404, json: { detail: "not stubbed" } });
  });

  await page.goto("/#attacks");
  await expect(page.getByRole("button", { name: /Crib constraints/ })).toBeVisible();

  const search = page.getByRole("searchbox", { name: "Search attacks" });
  await search.fill("no-such-attack");

  await expect(page.getByText("No attacks match.")).toBeVisible();
  await page.getByRole("button", { name: "clear search" }).click();

  await expect(search).toHaveValue("");
  await expect(page.getByRole("button", { name: /Crib constraints/ })).toBeVisible();
  await expect(page.getByText("No attacks match.")).toHaveCount(0);
});
