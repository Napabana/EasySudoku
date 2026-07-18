import { expect, test } from "@playwright/test";
import { chooseLanguage, gridValues, loadAndConfirmDemo } from "./helpers";

test("Solve requires confirmation, cancel preserves the board, and confirm fills it", async ({ page }) => {
  await chooseLanguage(page, "en-US");
  await loadAndConfirmDemo(page);
  const before = await gridValues(page);

  await page.getByTestId("solve-all").click();
  await expect(page.getByTestId("confirm-dialog")).toBeVisible();
  await page.getByTestId("confirm-cancel").click();
  expect(await gridValues(page)).toEqual(before);

  await page.getByTestId("solve-all").click();
  await page.getByTestId("confirm-accept").click();
  await expect.poll(async () => (await gridValues(page)).filter(Boolean).length).toBe(81);
});
