import { expect, type Page } from "@playwright/test";

export async function chooseLanguage(page: Page, locale: "en-US" | "zh-CN"): Promise<void> {
  await page.goto("/");
  const gate = page.getByTestId("language-gate");
  await expect(gate).toBeVisible();
  await gate.getByTestId(`language-${locale}`).click();
  await gate.locator("button").last().click();
  await expect(gate).toBeHidden();
}

export async function loadAndConfirmDemo(page: Page): Promise<void> {
  await page.getByTestId("load-demo").click();
  await expect(page.locator('input[data-cell="0-0"]')).toHaveValue("5");
  await page.getByTestId("confirm-board").click();
  await expect(page.locator('input[data-cell="0-0"]')).toHaveAttribute("readonly", "");
}

export async function gridValues(page: Page): Promise<string[]> {
  return page.locator("input[data-cell]").evaluateAll((inputs) => {
    return inputs.map((input) => (input as HTMLInputElement).value);
  });
}

export async function indexedDbHasCurrentImage(page: Page): Promise<boolean> {
  return page.evaluate(async () => {
    return new Promise<boolean>((resolve, reject) => {
      const request = indexedDB.open("easysudoku.images", 1);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction("images", "readonly");
        const get = tx.objectStore("images").get("current");
        get.onerror = () => reject(get.error);
        get.onsuccess = () => {
          resolve(Boolean(get.result));
          db.close();
        };
      };
    });
  });
}
