import { expect, test } from "@playwright/test";
import { chooseLanguage, loadAndConfirmDemo } from "./helpers";

test("Chinese mode localizes controls, explanation modes, and history", async ({ page }) => {
  await chooseLanguage(page, "zh-CN");

  await expect(page.getByTestId("load-demo")).toHaveText("加载示例盘面");
  await expect(page.getByTestId("confirm-board")).toHaveText("确认初始盘面");
  await expect(page.getByTestId("next-step")).toHaveText("推导下一步");
  await expect(page.getByTestId("mode-brief")).toHaveText("简洁");
  await expect(page.getByTestId("mode-teaching")).toHaveText("教学");
  await expect(page.getByTestId("mode-technical")).toHaveText("技术");

  await loadAndConfirmDemo(page);
  await page.getByTestId("next-step").click();
  await expect(page.getByTestId("history-item")).toHaveCount(1);

  const relevantText = await page.getByTestId("app-main").innerText();
  expect(relevantText).not.toMatch(/\b(?:Actions|Explanation|History|Brief|Teaching|Technical|Next step|Clear session)\b/);
});
