import { expect, test } from "@playwright/test";
import { chooseLanguage, loadAndConfirmDemo } from "./helpers";

test("invalid and blank images show localized errors", async ({ page }) => {
  test.setTimeout(60_000);
  await chooseLanguage(page, "zh-CN");

  await page.getByTestId("image-input").setInputFiles({
    name: "not-image.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("not an image")
  });
  await expect(page.getByTestId("explanation-panel")).toContainText("请选择支持的图片文件");

  const blankDataUrl = await page.evaluate(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 900;
    canvas.height = 900;
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas unavailable");
    context.fillStyle = "white";
    context.fillRect(0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/png");
  });
  await page.getByTestId("image-input").setInputFiles({
    name: "blank.png",
    mimeType: "image/png",
    buffer: Buffer.from(blankDataUrl.split(",")[1], "base64")
  });
  await expect(page.getByTestId("explanation-panel")).toContainText("未能从图片中识别出数独数字");
});

test("server and network failures are localized and duplicate requests are blocked", async ({ page }) => {
  await chooseLanguage(page, "en-US");
  await page.route("**/upload", (route) => route.fulfill({
    status: 500,
    contentType: "application/json",
    body: JSON.stringify({ detail: { code: "INTERNAL_ERROR" } })
  }));
  await page.getByTestId("image-input").setInputFiles({
    name: "image.png",
    mimeType: "image/png",
    buffer: Buffer.from("fake")
  });
  await expect(page.getByTestId("explanation-panel")).toContainText("Image recognition failed");
  await page.unroute("**/upload");

  await loadAndConfirmDemo(page);
  await page.route("**/next-step", (route) => route.abort("failed"));
  await page.getByTestId("next-step").click();
  await expect(page.getByTestId("explanation-panel")).toContainText("Request failed");
  await page.unroute("**/next-step");

  let requests = 0;
  await page.route("**/next-step", async (route) => {
    requests += 1;
    await new Promise((resolve) => setTimeout(resolve, 500));
    await route.fulfill({ status: 200, contentType: "application/json", body: "null" });
  });
  await page.getByTestId("next-step").click();
  await expect(page.getByTestId("next-step")).toBeDisabled();
  await page.getByTestId("next-step").click({ force: true });
  await expect.poll(() => requests).toBe(1);
});

test("responsive layouts keep the square board usable and unobstructed", async ({ page }) => {
  await chooseLanguage(page, "en-US");
  await loadAndConfirmDemo(page);
  await page.getByTestId("next-step").click();
  await expect(page.getByTestId("history-item")).toHaveCount(1);

  for (const viewport of [
    { width: 360, height: 800 },
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1440, height: 900 }
  ]) {
    await page.setViewportSize(viewport);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), `${viewport.width}x${viewport.height} overflow`).toBe(true);

    const board = page.getByTestId("sudoku-board");
    await board.scrollIntoViewIfNeeded();
    const box = await board.boundingBox();
    expect(box, `${viewport.width}x${viewport.height} board box`).not.toBeNull();
    expect(Math.abs((box?.width ?? 0) - (box?.height ?? 0)), `${viewport.width}x${viewport.height} square`).toBeLessThanOrEqual(2);
    const unobstructed = await board.evaluate((element) => {
      const rect = element.getBoundingClientRect();
      const top = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
      return Boolean(top && element.contains(top));
    });
    expect(unobstructed, `${viewport.width}x${viewport.height} board coverage`).toBe(true);

    await page.getByTestId("next-step").scrollIntoViewIfNeeded();
    await expect(page.getByTestId("next-step")).toBeVisible();
    await page.getByTestId("history-item").scrollIntoViewIfNeeded();
    await expect(page.getByTestId("history-item")).toBeEnabled();
  }
});
