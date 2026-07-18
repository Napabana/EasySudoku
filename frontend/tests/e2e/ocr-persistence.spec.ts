import path from "node:path";
import { expect, test } from "@playwright/test";
import { chooseLanguage, indexedDbHasCurrentImage } from "./helpers";

const demoImage = path.resolve(process.cwd(), "../examples/demo_sudoku.png");

test("fixed OCR image uploads, remains editable, and can be confirmed", async ({ page }) => {
  test.setTimeout(60_000);
  await chooseLanguage(page, "en-US");

  const uploadResponse = page.waitForResponse((response) => response.url().endsWith("/upload"));
  await page.getByTestId("image-input").setInputFiles(demoImage);
  expect((await uploadResponse).status()).toBe(200);
  await expect(page.locator('input[data-cell="0-0"]')).toHaveValue("5");

  await page.locator('input[data-cell="0-0"]').fill("4");
  await expect(page.locator('input[data-cell="0-0"]')).toHaveValue("4");
  await page.locator('input[data-cell="0-0"]').fill("5");
  await page.getByTestId("confirm-board").click();
  await expect(page.locator('input[data-cell="0-0"]')).toHaveAttribute("readonly", "");
});

test("board, history, language, mode, and image restore; clear removes session stores", async ({ page }) => {
  test.setTimeout(60_000);
  await chooseLanguage(page, "en-US");
  await page.getByTestId("image-input").setInputFiles(demoImage);
  await expect(page.locator('input[data-cell="0-0"]')).toHaveValue("5");
  await page.getByTestId("confirm-board").click();
  await page.getByTestId("next-step").click();
  await expect(page.getByTestId("history-item")).toHaveCount(1);
  await page.getByTestId("language-zh-CN").click();
  await page.getByTestId("mode-technical").click();
  await expect.poll(() => indexedDbHasCurrentImage(page)).toBe(true);

  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("lang", "zh-CN");
  await expect(page.getByTestId("mode-technical")).toHaveText("技术");
  await expect(page.getByTestId("history-item")).toHaveCount(1);
  await expect(page.locator('input[data-cell="0-0"]')).toHaveValue("5");
  expect(await indexedDbHasCurrentImage(page)).toBe(true);

  await page.getByTestId("clear-session").click();
  await page.getByTestId("confirm-accept").click();
  await expect(page.getByTestId("history-empty")).toBeVisible();
  await expect.poll(() => page.evaluate(() => localStorage.getItem("easysudoku.session.v1"))).toBeNull();
  await expect.poll(() => indexedDbHasCurrentImage(page)).toBe(false);
});
