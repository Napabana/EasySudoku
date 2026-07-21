import { expect, test, type Locator } from "@playwright/test";
import { chooseLanguage, loadAndConfirmDemo } from "./helpers";

async function expectCurrentItemVisible(list: Locator): Promise<void> {
  await expect.poll(async () => {
    return list.locator("[data-current='true']").evaluate((item, element) => {
      const itemRect = item.getBoundingClientRect();
      const listRect = element.getBoundingClientRect();
      return itemRect.top >= listRect.top - 1 && itemRect.bottom <= listRect.bottom + 1;
    }, await list.elementHandle());
  }).toBe(true);
}

test("history stays bounded and keeps the selected step visible", async ({ page }) => {
  test.setTimeout(90_000);
  await page.setViewportSize({ width: 1440, height: 900 });
  await chooseLanguage(page, "en-US");

  await expect(page.getByTestId("history-empty")).toBeVisible();
  await loadAndConfirmDemo(page);

  let panelHeightAtTwo = 0;
  for (let count = 1; count <= 10; count += 1) {
    await page.getByTestId("next-step").click();
    await expect(page.getByTestId("history-item")).toHaveCount(count);
    if (count === 2) {
      panelHeightAtTwo = await page.getByTestId("history-panel").evaluate((element) => element.getBoundingClientRect().height);
    }
  }

  const list = page.getByTestId("history-list");
  const desktopLayout = await list.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      clientHeight: element.clientHeight,
      scrollHeight: element.scrollHeight,
      clientWidth: element.clientWidth,
      scrollWidth: element.scrollWidth,
      overflowX: style.overflowX,
      overflowY: style.overflowY
    };
  });
  expect(desktopLayout.clientHeight).toBe(224);
  expect(desktopLayout.scrollHeight).toBeGreaterThan(desktopLayout.clientHeight);
  expect(desktopLayout.scrollWidth).toBeLessThanOrEqual(desktopLayout.clientWidth);
  expect(desktopLayout.overflowX).toBe("hidden");
  expect(desktopLayout.overflowY).toBe("auto");
  expect(await page.getByTestId("history-panel").evaluate((element) => element.getBoundingClientRect().height)).toBeCloseTo(panelHeightAtTwo, 0);

  for (const index of [0, 4, 9]) {
    await page.getByTestId("history-item").nth(index).click();
    await expect(page.getByTestId("history-item").nth(index)).toHaveAttribute("data-current", "true");
    await expectCurrentItemVisible(list);
  }

  await page.setViewportSize({ width: 390, height: 844 });
  expect(await list.evaluate((element) => element.clientHeight)).toBe(208);
  expect(await list.evaluate((element) => element.scrollWidth <= element.clientWidth)).toBe(true);
  await page.getByTestId("history-item").first().click();
  await expectCurrentItemVisible(list);
  await page.getByTestId("language-zh-CN").click();
  await expect(page.getByTestId("history-panel")).toContainText("第 1 / 10 步");

  await page.waitForTimeout(350);
  await page.reload();
  await expect(page.getByTestId("history-item")).toHaveCount(10);
  await expect(page.getByTestId("history-item").first()).toHaveAttribute("data-current", "true");
  await expectCurrentItemVisible(page.getByTestId("history-list"));
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
});
