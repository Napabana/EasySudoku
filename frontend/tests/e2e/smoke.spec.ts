import { expect, test } from "@playwright/test";

const puzzle = [
  [5, 3, 0, 0, 7, 0, 0, 0, 0],
  [6, 0, 0, 1, 9, 5, 0, 0, 0],
  [0, 9, 8, 0, 0, 0, 0, 6, 0],
  [8, 0, 0, 0, 6, 0, 0, 0, 3],
  [4, 0, 0, 8, 0, 3, 0, 0, 1],
  [7, 0, 0, 0, 2, 0, 0, 0, 6],
  [0, 6, 0, 0, 0, 0, 2, 8, 0],
  [0, 0, 0, 4, 1, 9, 0, 0, 5],
  [0, 0, 0, 0, 8, 0, 0, 7, 9]
];

async function chooseEnglish(page) {
  await page.goto("/");
  await page.getByRole("button", { name: "English" }).first().click();
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByRole("heading", { name: "Sudoku Board" })).toBeVisible();
}

async function fillPuzzle(page) {
  for (let row = 0; row < 9; row += 1) {
    for (let col = 0; col < 9; col += 1) {
      const value = puzzle[row][col];
      if (value) {
        await page.locator(`input[data-cell="${row}-${col}"]`).fill(String(value));
      }
    }
  }
}

test("main solving flow persists and clears", async ({ page }) => {
  await chooseEnglish(page);
  await fillPuzzle(page);

  await page.getByRole("button", { name: "Confirm givens" }).click();
  await expect(page.getByText("✓ Puzzle locked")).toBeVisible();

  await page.getByRole("button", { name: "Next step" }).click();
  await expect(page.getByText("Step 1 of 1")).toBeVisible();
  await expect(page.getByText("Target", { exact: true })).toBeVisible();

  await page.locator('input[data-cell="0-2"]').click();
  await page.getByRole("button", { name: "Hint selected cell" }).click();
  await expect(page.getByText(/Candidates for|Cell/)).toBeVisible();

  await page.getByRole("button", { name: "Back" }).click();
  await page.getByRole("button", { name: "Forward" }).click();
  await expect(page.getByText("Step 1 of 1")).toBeVisible();

  await page.reload();
  await expect(page.getByText("Step 1 of 1")).toBeVisible();
  await expect(page.getByText("✓ Puzzle locked")).toBeVisible();

  await page.getByRole("button", { name: "Clear session" }).click();
  await page.getByRole("button", { name: "Clear session" }).last().click();
  await expect(page.getByText("No deduction history yet.")).toBeVisible();
});

test("responsive layouts do not create horizontal overflow", async ({ page }) => {
  await chooseEnglish(page);
  for (const viewport of [
    { width: 360, height: 800 },
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1440, height: 900 }
  ]) {
    await page.setViewportSize(viewport);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(overflow, `${viewport.width}x${viewport.height}`).toBe(false);
  }
});
