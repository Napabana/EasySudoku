# EasySudoku 演示脚本

目标时长：2-3 分钟。

## 一句话定位

EasySudoku 是一个可解释的数独推导导师。用户上传一张数独照片后，系统会识别盘面，并像老师一样一步一步解释下一步为什么成立。

## 演示流程

1. 打开项目首页。
   - 说明：这是一个 Vue + FastAPI Web App，支持桌面和手机端。

2. 切换语言。
   - 先展示中文，再切到英文。
   - 强调：UI、规则名、解释文本都支持中英文。

3. 上传数独图片。
   - 选择一张准备好的测试图片。
   - OCR 完成后展示识别盘面。
   - 如果有识别错误，手动修正一两个格子。

4. 确认初始盘面。
   - 点击 `Confirm givens / 确认初始盘面`。
   - 指出初始数字被锁定，后续推导不会误改。

5. 展示候选数和选中格。
   - 点击一个空格。
   - 展示蓝色选中框、同行/同列/同宫弱高亮、候选数 3x3 布局。

6. 执行下一步。
   - 点击 `Next step / 推导下一步`。
   - 展示当前目标格、黄色目标背景、历史新增一项。

7. 讲解解释面板。
   - 展示 `Target / Conclusion / Why / Verification` 分组。
   - 切换 Brief / Teaching / Technical。
   - 说明：人类规则优先，复杂情况由 SMT 验证兜底。

8. 历史回放。
   - 点击 Back / Forward。
   - 点击历史卡片跳转。
   - 说明：每一步保存完整盘面状态。

9. 刷新恢复。
   - 刷新页面。
   - 展示盘面、历史、语言、解释模式被恢复。
   - 说明：盘面和设置保存在 localStorage，上传图片保存在 IndexedDB。

10. 可选：完整求解。
    - 点击 Solve。
    - 展示确认弹窗，避免误操作。

## 技术亮点

- 本地 OCR：OpenCV 透视变换 + ONNX 数字模型，无需外部 OCR 服务。
- 可解释推导：Hidden Single / Naked Pair 等人类规则优先。
- SMT 兜底：Z3 UNSAT Core 用于验证复杂排除。
- 结构化协议：后端返回 `step.rule_type`、`target_cell`、`candidate_changes`、`verification_type`，前端负责 i18n 解释。
- 前端体验：Vue 3 + TypeScript + Tailwind，候选数、历史、刷新恢复和响应式布局。
- 自动化验证：Playwright smoke test 覆盖主流程和移动端横向溢出。

## 录制前检查

```bash
cd ~/EasySudoku/frontend
npm install
npm run build

cd ~/EasySudoku
source venv312/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

另开终端：

```bash
cd ~/EasySudoku/frontend
EASYSUDOKU_BASE_URL=http://127.0.0.1:8000 npm run test:smoke
```

确认 smoke test 通过后再录制。
