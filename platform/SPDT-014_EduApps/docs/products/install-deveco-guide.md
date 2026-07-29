# DevEco Studio 安装指南

> 预计人工耗时：30-45 分钟（含下载等待）

---

## Step 1：下载（5 分钟操作 + 等待下载）

1. 打开：https://developer.huawei.com/consumer/cn/download/deveco-studio
2. 登录华为开发者账号（没有就注册一个，免费）
3. 下载 **DevEco Studio 5.0.x for Windows**
4. 等待下载完成（约 2-4 GB）

## Step 2：安装（10 分钟）

1. 运行 `deveco-studio-5.x.x.x.exe`
2. 一路 Next（默认路径即可：`C:\Users\{用户名}\AppData\Local\Huawei\DevEcoStudio`）
3. **License Agreement** → 勾选同意 → Next
4. 安装完成后**勾选「Run DevEco Studio」**→ Finish

## Step 3：首次配置 SDK（10 分钟）

1. DevEco Studio 首次启动会弹出 **SDK Setup Wizard**
2. 选择 **HarmonyOS** → 勾选最新 API Version（如 5.0.3(15)）
3. 点击 **Apply** → 等待 SDK 下载完成
4. 完成后点击 **Finish**

## Step 4：验证安装

```powershell
cd D:\9_infra\harmony_workshop
.\scripts\verify-deveco.ps1
```

看到 `✅ 环境就绪` 即安装成功。

## Step 5：编译第一个 App

```powershell
.\scripts\dev-loop.ps1 -ProjectPath .\apps\craftsman-utils
```

如果编译报错，将 `build-error.log` 的内容发给我，我来分析和修复代码。

---

### 可选：安装真机驱动

如果要真机测试（非模拟器）：
- 手机：设置 → 关于手机 → 连续点击「版本号」7次 → 开启开发者模式
- 回到设置 → 系统 → 开发者选项 → 开启「USB 调试」
- 用数据线连接电脑 → 手机上点「允许」

---

### 如果遇到问题

把错误截图或错误信息发给我，我来诊断。
