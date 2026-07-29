# 1、DevEco CLI 工具详解与 DevEco Code 对比

**问题详情：**

鸿蒙 APP 开发推出了 deveco cli 助手，请简介该工具，包括对比与 deveco code 的区别和联系，以及实际开发时的流程。

---

# DevEco CLI 完整介绍（含与 DevEco Code 对比、实战开发流程）

## 一、DevEco CLI 工具简介

### 1. 基础定位

DevEco CLI（命令：`devecocli`）是 HDC2026 随 HarmonyOS 7（API26）发布的**鸿蒙标准化命令行开发工具**，npm 全局安装的轻量化工具包，本质是把 DevEco Studio 底层全套工具链封装为可被脚本、AI Agent 调用的原子化命令集Harmo...。
 简单比喻：**DevEco Code 是 AI 大脑，DevEco CLI 是执行手脚**，专门负责落地所有工程实操动作。

![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%27256%27%20height=%27192%27/%3e)![image](https://p3-flow-imagex-sign.byteimg.com/labis/image/6fc6914924ce3f90d36f045e78b64c76~tplv-a9rns2rl98-pc_smart_face_crop-v1:512:384.image?lk3s=8e244e95&rcl=20260716143218F242D2289909302546FD&rrcfp=cee388b0&x-expires=2099543547&x-signature=fyjq9WvXYoz52UTa3mTOAMkEZgw%3D)

### 2. 底层整合能力

内置统一封装鸿蒙全套原生工具，无需单独配置：

- `hvigor`：鸿蒙构建编译工具（打包 HAP/HSP）
- `ohpm`：鸿蒙三方包管理器
- `hdc`：真机 / 模拟器连接调试工具（类似 adb）
- `emulator`：模拟器镜像下载、启停管理
- `hilog`：应用运行日志抓取、过滤 同时附加能力：项目脚手架、代码 lint 校验、本地鸿蒙官方文档检索、MCP 协议服务、AI Skill 插件管理。

### 3. 核心价值场景

1. **自动化流水线**：CI/CD、批量打包、批量多设备测试，完全脱离 IDE 图形界面；
2. **第三方 AI Agent 接入**：Cursor、Claude Code、自研多智能体集群可直接调用 CLI 完成完整开发闭环；
3. **终端极简开发**：Vscode + 终端轻量化写鸿蒙，不用打开重型 DevEco Studio；
4. **批量工程管理**：批量创建模块、升级 SDK、签名打包、版本发布。

### 4. 安装方式

```bash
# 全局安装
npm install -g @deveco/deveco-cli
# 校验安装
devecocli --version
# 一键对接AI智能体（注入鸿蒙开发技能）
devecocli init
```

### 5. 高频核心命令速览

```bash
devecocli create      # 脚手架新建应用/模块
devecocli build       # 编译构建HAP包
devecocli run         # 编译+安装+启动应用
devecocli device list # 查看连接真机
devecocli emulator    # 模拟器镜像管理、启动
devecocli log         # 过滤抓取应用日志
devecocli lint        # ArkTS代码语法校验
devecocli docs        # 检索鸿蒙官方开发文档
devecocli update      # 升级CLI工具本身
```

## 二、DevEco CLI vs DevEco Code：区别与联系

### （一）核心区别对照表

| 对⁠比⁠维⁠度 | DevEco Code | DevEco CLI |
| --- | --- | --- |
| **角⁠色⁠定⁠位** | 鸿⁠蒙 AI 编⁠程⁠智⁠能⁠体（大⁠脑） | 命⁠令⁠行⁠执⁠行⁠工⁠具⁠集（机⁠械⁠手） |
| **交⁠互⁠形⁠式** | 图⁠形 / 对⁠话⁠式 AI 助⁠手，自⁠然⁠语⁠言⁠交⁠互 | 纯⁠终⁠端⁠命⁠令、程⁠序 API 调⁠用，无 UI |
| **核⁠心⁠能⁠力** | 需⁠求⁠拆⁠解、架⁠构⁠设⁠计、ArkTS 代⁠码⁠生⁠成、报⁠错⁠智⁠能⁠修⁠复、UI 生⁠成、测⁠试⁠用⁠例⁠生⁠成、问⁠题⁠推⁠理 | 项⁠目⁠创⁠建、编⁠译⁠打⁠包、设⁠备⁠管⁠理、推⁠包⁠运⁠行、日⁠志⁠采⁠集、构⁠建⁠自⁠动⁠化、CI 执⁠行 |
| **目⁠标⁠用⁠户** | 独⁠立⁠开⁠发⁠者、新⁠手，开⁠箱⁠即⁠用⁠一⁠站⁠式 AI 开⁠发 | 企⁠业⁠研⁠发、自⁠动⁠化⁠工⁠程⁠师、AI 工⁠具⁠开⁠发⁠者、终⁠端⁠重⁠度⁠使⁠用⁠者 |
| **依⁠赖⁠关⁠系** | 主⁠动⁠调⁠用 CLI 完⁠成⁠工⁠程⁠落⁠地，必⁠须⁠依⁠赖 CLI 才⁠能⁠真⁠机⁠运⁠行 | 可⁠独⁠立⁠使⁠用（纯⁠命⁠令⁠行⁠开⁠发），无 AI 依⁠赖 |
| **部⁠署⁠形⁠态** | 集⁠成 DevEco Studio 插⁠件 / 独⁠立⁠客⁠户⁠端 | npm 全⁠局⁠命⁠令⁠行，轻⁠量⁠无⁠图⁠形⁠环⁠境 |
| **使⁠用⁠场⁠景** | 写⁠代⁠码、答⁠疑、逻⁠辑⁠重⁠构、需⁠求⁠转⁠工⁠程 | 自⁠动⁠化⁠流⁠水⁠线、Agent 调⁠度、批⁠量⁠运⁠维、轻⁠量⁠化⁠编⁠译⁠部⁠署 |

### （二）二者内在联系

1. **上下层协作关系** 完整 AI 开发链路：用户自然语言需求 → DevEco Code 分析生成代码 → DevEco CLI 执行构建、真机运行、抓取日志 → DevEco Code 读取日志自动修复代码，形成闭环。
2. **底层同源** 两者均复用 DevEco Studio 原生工具链、统一鸿蒙知识库、官方 Skills 能力，底层编译、设备通信逻辑完全一致，工程文件互相兼容。
3. **两种组合使用模式**

- 模式 1（AI 全流程）：DevEco Code 生成代码 + CLI 自动构建调试（主流 AI 开发方案）
- 模式 2（纯终端）：仅 CLI，搭配 VSCode 手动编码，无 AI 参与

## 三、DevEco CLI 完整实战开发流程

分为**纯命令行独立开发流程**、**DevEco Code+CLI AI 协同流程**两套主流工作流。

### 流程一：纯 DevEco CLI 终端开发（无 IDE / 无 AI）

#### 步骤 1：环境前置准备

1. 安装 Node.js（npm 依赖）、完整 DevEco Studio（提供 SDK、模拟器镜像）
2. npm 全局安装`@deveco/deveco-cli`
3. 连接真机 / 下载模拟器镜像

```bash
# 下载手机模拟器镜像
devecocli emulator image download --device-type phone --os-version "HarmonyOS 6.0.1(21)"
```

#### 步骤 2：创建鸿蒙工程 / 业务模块

```bash
# 创建基础应用，空Ability模板
devecocli create MyHarmonyApp --app-name MyHarmonyApp --template empty-ability
# 进入项目目录
cd MyHarmonyApp
# 新增HSP共享模块
devecocli create user_module --template har
```

#### 步骤 3：编码与代码校验

使用 VSCode 打开项目手写 ArkTS/ArkUI 代码，完成后执行语法检查：

```bash
# 全工程代码校验，输出错误警告
devecocli lint
```

#### 步骤 4：编译构建应用包

```bash
# Debug增量编译
devecocli build --incremental --mode debug
# Release正式打包（支持自动签名，需提前配置证书）
devecocli build --mode release --sign ./sign_config.json
```

#### 步骤 5：设备部署与运行

```bash
# 查看所有可用设备（真机+模拟器）
devecocli device list
# 一键编译+安装+启动应用（最简命令）
devecocli run --device 设备ID
# 仅安装已编译好的hap包
devecocli deploy --hap ./entry/build/outputs/hap/entry-debug.hap
```

![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%27256%27%20height=%27192%27/%3e)![image](https://p11-flow-imagex-sign.byteimg.com/isp-i18n-media/image/8649a26fce6e53e157979bf887faaae5~tplv-a9rns2rl98-pc_smart_face_crop-v1:512:384.image?lk3s=8e244e95&rcl=20260716143218F242D2289909302546FD&rrcfp=cee388b0&x-expires=2099543576&x-signature=Gln6JHUeZY4oKItAFGfQCiBz%2B2Q%3D)

#### 步骤 6：调试日志排查问题

```bash
# 实时抓取当前应用日志，过滤应用包名
devecocli log --filter com.example.myharmonyapp
```

#### 步骤 7：打包发布产物

```bash
# 输出可上架标准hap/ark包
devecocli package --output ./dist/release
```

### 流程二：DevEco Code + DevEco CLI AI 协同自动化流程（Agent 开发主流）

1. **需求输入**：在 DevEco Code 输入自然语言需求（如 “做一个鸿蒙待办清单应用，含增删改查”）
2. **AI 规划生成**：DevEco Code 自动拆分架构、生成页面、逻辑、路由、权限配置代码，写入工程目录
3. **自动调用 CLI 校验**：Code 内部自动执行`devecocli lint`，发现语法问题即时修复代码
4. **调用 CLI 编译部署**：自动执行`devecocli run`，编译并推送到模拟器 / 真机启动
5. **日志回传分析**：CLI 抓取运行日志返回 DevEco Code，AI 自动定位崩溃、UI 异常、接口报错
6. **迭代循环**：AI 修改代码 → 再次调用 CLI 构建运行，直至功能符合验收标准
7. **最终打包**：AI 调用 CLI 执行 release 打包，输出发布包

## 四、工具适用场景总结

1. 只用 DevEco CLI：自动化 CI 流水线、服务器批量构建、终端极简开发、自研 AI Agent 调度；
2. 只用 DevEco Code：新手快速写代码、日常业务开发、纯 AI 生成应用；
3. Code+CLI 组合：AI 全自动 Agentic 开发、需求到真机一键闭环、大规模多模块迭代。

需要我把上述流程整理成一份可直接复制使用的**CLI 批量脚本模板**（创建项目 + 编译 + 运行 + 日志一条龙）吗？

---

# 2、DevEco CLI 实现 AI 自动化开发闭环

**问题详情：**

我深度采用 AI 编程，在针对鸿蒙 APP 编程时，我觉得 deveco ide 需要人工操作（比如，总是需要人类来点击 build, run 等按钮，以及反馈 log error 等），大大的降低了自动化程度。使用纯 DevEco CLI 是否能减少人工操作，使得本地 AI 编程工具能够全自动完成鸿蒙 APP 的编程？ 人工仅在使用 APP 并反馈问题方面介入。

---

# 结论先行

**纯 DevEco CLI 完全可以彻底消除 DevEco IDE 手动点击操作，实现本地 AI 编程工具全自动鸿蒙开发闭环**，编译、运行、抓日志、报错修复、打包全流程无人工介入；你只需要在设备上体验 App，反馈功能 / UI 问题即可。
 DevEco IDE 的「点击 Build、点击 Run、手动查看日志、手动切换设备」等人工操作全部可被 CLI 命令程序化替代，专门面向 AI Agent 自动化设计。

## 一、为什么 DevEco IDE 自动化短板，CLI 能完全解决

### 1. DevEco Studio（IDE）天生依赖人工交互的痛点

1. 图形界面驱动：构建、部署、日志面板、设备选择全靠鼠标点击，无法被脚本 / AI 自动调用；
2. 输出非结构化：报错、日志分散在弹窗、底部控制台，机器很难批量读取解析；
3. 大量前置弹窗确认：设备授权、签名登录、SDK 下载、模拟器启动均需人工确认；
4. 流程割裂：代码生成、校验、编译、运行、日志排查分散在不同面板，无法串联自动循环。

### 2. DevEco CLI 为 AI 自动化原生设计的核心优势

1. **全流程原子化可调用命令**
   把 IDE 所有手动操作拆成无交互、可脚本调用指令，无弹窗、无需人工确认：
   - 工程创建：`devecocli create` 自动生成标准鸿蒙工程，无需手动选模板
   - 静态语法检查：`devecocli lint` 输出结构化 JSON 报错，AI 直接解析
   - 编译构建：`devecocli build` 自动驱动 Hvigor，支持预配置签名，全程静默打包
   - 设备自动管理：`device list` 自动获取真机 / 模拟器 ID，无需手动下拉选择设备
   - 一键部署运行：`devecocli run` = 编译 + 安装 + 启动应用，单命令全自动
   - 结构化日志采集：`devecocli log` 过滤应用包名，输出崩溃、异常、业务日志给 AI
   - 模拟器无人值守：`emulator start` 后台启动，无需打开 IDE 模拟器窗口
   CSDN博...
2. **机器友好输出**
   所有命令支持 `--json` 参数，构建失败、编译报错、运行崩溃全部输出标准 JSON，AI 编程工具（Cursor、自研多 Agent、DevEco Code）可直接解析，不用人工阅读文本日志51CTO。
3. **无 GUI 依赖**
   本地可以完全不启动 DevEco Studio 图形界面，仅依赖底层 SDK、JDK、Node 环境即可完成完整开发；服务器 CI / 本地 AI 流水线都能跑。
4. **支持 MCP 协议对接 AI 工具**
   `devecocli init --agent xxx` 一键把全套鸿蒙开发能力注册为 AI 工具的可调用 Skill，AI 可以自主循环：生成代码→校验→编译→运行→读日志→自动修复代码，形成自迭代闭环。

## 二、DevEco CLI 对比 DevEco IDE：自动化能力差异

| 开⁠发⁠环⁠节 | DevEco Studio IDE（传⁠统⁠方⁠式） | 纯 DevEco CLI（AI 全⁠自⁠动⁠流⁠水⁠线） |
| --- | --- | --- |
| 项⁠目⁠初⁠始⁠化 | 手⁠动⁠新⁠建、选⁠择⁠模⁠板、填⁠写⁠包⁠名 | `devecocli create` 脚⁠本⁠自⁠动⁠创⁠建，参⁠数⁠批⁠量⁠配⁠置 |
| 代⁠码⁠语⁠法⁠校⁠验 | 保⁠存⁠后⁠手⁠动⁠看⁠底⁠部⁠警⁠告，无⁠结⁠构⁠化⁠输⁠出 | `lint` 命⁠令⁠批⁠量⁠扫⁠描，JSON 格⁠式⁠错⁠误⁠返⁠回 AI |
| 编⁠译 Build | 鼠⁠标⁠点⁠击 Build 按⁠钮，弹⁠窗⁠等⁠待⁠构⁠建 | `build` 静⁠默⁠后⁠台⁠编⁠译，自⁠动⁠读⁠取⁠预⁠配⁠置⁠签⁠名⁠文⁠件，无⁠弹⁠窗 |
| 设⁠备⁠选⁠择 | 下⁠拉⁠框⁠手⁠动⁠选⁠真⁠机 / 模⁠拟⁠器 | `device list` 自⁠动⁠枚⁠举⁠设⁠备，脚⁠本⁠自⁠动⁠选⁠用⁠第⁠一⁠个⁠可⁠用⁠设⁠备 |
| 安⁠装⁠运⁠行 Run | 点⁠击 Run 按⁠钮，等⁠待⁠弹⁠窗⁠安⁠装、启⁠动 | `run` 一⁠键⁠完⁠成⁠编⁠译、安⁠装、权⁠限⁠配⁠置、启⁠动⁠应⁠用 |
| 日⁠志⁠查⁠看⁠排⁠错 | 切⁠换 Log 窗⁠口，手⁠动⁠筛⁠选⁠包⁠名，人⁠工⁠阅⁠读⁠报⁠错 | `log` 命⁠令⁠定⁠向⁠抓⁠取⁠应⁠用⁠日⁠志，结⁠构⁠化⁠传⁠给 AI 自⁠动⁠分⁠析⁠崩⁠溃⁠原⁠因 |
| 模⁠拟⁠器⁠启⁠动 | 打⁠开 IDE 模⁠拟⁠器⁠面⁠板、手⁠动⁠启⁠动⁠镜⁠像 | `emulator start` 后⁠台⁠静⁠默⁠启⁠动，无⁠需 GUI |
| 打⁠包 Release | 手⁠动⁠配⁠置⁠签⁠名、点⁠击⁠打⁠包、手⁠动⁠复⁠制⁠产⁠物 | `build --mode release` 读⁠取⁠本⁠地⁠签⁠名⁠配⁠置⁠文⁠件，自⁠动⁠输⁠出 HAP/APP 包 |
| 流⁠程⁠自⁠动⁠化 | 无⁠法⁠串⁠联⁠循⁠环，每⁠一⁠步⁠必⁠须⁠人⁠工⁠触⁠发 | 可⁠写⁠入⁠脚⁠本 / AI Agent 循⁠环，自⁠动「改⁠代⁠码→构⁠建→运⁠行→修⁠复」多⁠轮⁠迭⁠代 |
| AI 集⁠成⁠模⁠式 | 内⁠置 DevEco Code 但⁠仍⁠需 IDE 窗⁠口⁠承⁠载 | 独⁠立 MCP 服⁠务，任⁠何⁠本⁠地 AI 编⁠辑⁠器⁠均⁠可⁠无⁠缝⁠调⁠用，完⁠全⁠脱⁠离 IDE |

## 三、纯 DevEco CLI + 本地 AI 工具：全自动开发完整流程（零人工操作，仅最后体验反馈）

### 前置一次性配置（仅首次环境搭建需要人工，后续全程自动化）

1. 安装 Node.js、JDK、鸿蒙 SDK，配置 SDK 路径到 CLI：`devecocli config set sdk.path xxx`
2. 本地导出调试签名文件，写入`sign_config.json`，CLI 编译时自动读取，无需登录弹窗
3. AI 工具（Cursor / 自研 Agent）执行 `devecocli init --agent=xxx`，挂载 CLI 全部开发技能
4. 真机开启 USB 调试并完成一次授权（仅一次，后续 CLI 自动识别设备无需重复确认）

### 全自动闭环（人工仅输入需求 + 最后体验反馈问题）

#### 阶段 1：AI 接收需求，自动初始化工程（无人工）

本地 AI 接收自然语言需求（如 “开发鸿蒙待办 APP，支持增删改查、本地持久化存储”）
 AI 自主调用：

```bash
# 自动创建标准鸿蒙entry工程
devecocli create TodoApp --app-name com.example.todo --template empty-ability
```

#### 阶段 2：AI 生成全部 ArkTS/ArkUI 代码，自动语法校验（无人工）

AI 生成页面、路由、数据库逻辑代码写入工程目录，随即自动调用校验：

```bash
devecocli lint --project ./TodoApp --json
```

读取 JSON 报错，AI 自动修正语法、类型、API 版本问题，循环至无静态错误。

#### 阶段 3：全自动编译、部署、启动应用（替代手动点 Run，无人工）

AI 执行一体化运行命令，自动完成构建 + 签名 + 安装 + 启动：

```bash
devecocli run --project ./TodoApp --auto-select-device --sign ./sign_config.json
```

- `--auto-select-device`：自动选用第一个在线真机 / 模拟器，无需人工选择设备
- 自动读取本地签名配置，不会弹出账号登录弹窗

#### 阶段 4：自动抓取运行日志，AI 自主分析崩溃 / 业务异常（无需人工看日志面板）

应用启动后，AI 持续调用日志采集命令，过滤自身应用日志：

```bash
devecocli log --filter com.example.todo --json --once
```

1. 日志中存在闪退、报错、渲染异常 → AI 解析错误堆栈，自动修改对应代码文件
2. 自动回到阶段 3 重新编译运行，反复迭代至应用无崩溃、逻辑正常
3. 全程无需人工查看日志、定位报错、手动修改代码

#### 阶段 5：AI 输出可安装发布包（如需）

验证功能稳定后，AI 自动执行 Release 打包：

```bash
devecocli build --mode release --sign ./sign_config.json
```

产物自动输出到`./dist/release`目录。

#### 唯一人工介入环节

1. 初始需求描述（一次性输入）
2. 手机 / 模拟器打开 AI 自动部署好的 App，人工体验后反馈：
   - UI 样式不符合预期
   - 功能逻辑缺失 / 交互 bug
3. 反馈文本回传给 AI，再次触发完整自动化修复闭环

## 四、当前仅存少量无法完全自动化的边界场景（极少，可提前规避）

1. **首次真机调试授权**：手机弹出 “允许 USB 调试” 仅第一次需要手动点允许，后续永久免确认；模拟器无此步骤。
2. **线上正式发布签名**：商用上架 AGC 的正式证书需人工在开发者平台下载一次，保存本地配置后 CLI 可永久自动调用。
3. **特殊硬件权限弹窗**：相机、定位等敏感权限首次打开会在设备弹窗，可提前在工程配置预置权限，或 AI 自动注入代码静默申请。
4. **SDK 缺失下载**：CLI 检测 SDK 版本缺失时，可提前脚本预下载对应镜像，避免弹出下载确认窗口。

## 五、适配你的深度 AI 编程架构建议

如果你自研多智能体 / 本地 AI 编程集群，推荐采用这套分层架构实现极致自动化：

1. **上层 AI 规划 Agent**：负责需求拆解、代码生成、报错逻辑修复
2. **底层执行层：DevEco CLI**：统一封装所有鸿蒙工程操作，作为 AI 的标准化执行接口
3. **闭环逻辑**

```plaintext
用户需求反馈 → AI生成/修改代码 → CLI lint校验 → CLI build编译 → CLI run部署运行 → CLI log采集异常 → AI自动修复代码（循环）
```

完全规避 DevEco IDE 图形界面带来的人工点击、弹窗、手动操作损耗，实现你想要的**AI 全权负责开发，人只负责验收反馈**的模式。

需要我给你一份可直接嵌入 AI 工具的**全自动开发 Shell 脚本**（创建项目→lint→build→run→日志采集一体化，含 JSON 结构化输出参数）吗？

---

# 3、鸿蒙全自动开发 Shell 脚本

---

# DevEco CLI 鸿蒙全自动开发 Shell 脚本

## 说明

1. 适配 Linux /macOS；Windows 可改用 Git Bash / WSL 运行
2. 全程 JSON 结构化输出，方便本地 AI 工具解析报错、日志
3. 无人工弹窗、自动选设备、内置签名配置、自动循环修复可对接 AI
4. 分为 3 个脚本：
   - `hm_auto_init.sh`：自动新建鸿蒙项目
   - `hm_auto_build_run.sh`：校验 + 编译 + 部署运行 + 导出日志
   - `hm_auto_release_package.sh`：正式打包 Release 产物

## 前置一次性配置（仅执行 1 次）

新建 `config.env` 放在脚本同目录

```env
# config.env
# 鸿蒙SDK根目录
SDK_PATH="/Users/xxx/Library/Huawei/Sdk"
# 调试签名配置文件路径
SIGN_CONFIG="./sign_config.json"
# 应用包名
APP_BUNDLE="com.example.autoapp"
# 模拟器/设备自动选择：true自动取第一个在线设备
AUTO_DEVICE=true
# 日志输出文件
LOG_OUT="./runtime_log.json"
# 构建产物目录
DIST_DIR="./dist"
```

---

## 1. hm_auto_init.sh 项目自动创建脚本

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 2 ]; then
    echo "用法：$0 项目名称 模板名"
    echo "模板可选：empty-ability / har / library"
    exit 1
fi

PROJECT_NAME=$1
TEMPLATE=$2

echo "===== 自动创建鸿蒙工程：${PROJECT_NAME} ====="
devecocli create "${PROJECT_NAME}" \
  --app-name "${APP_BUNDLE}" \
  --template "${TEMPLATE}" \
  --sdk-path "${SDK_PATH}"

if [ $? -eq 0 ]; then
  echo "[SUCCESS] 项目创建完成，目录：./${PROJECT_NAME}"
else
  echo "[ERROR] 项目创建失败"
  exit 1
fi
```

### 使用示例

```bash
chmod +x hm_auto_init.sh
./hm_auto_init.sh AutoTodoApp empty-ability
```

---

## 2. hm_auto_build_run.sh 核心自动化流水线（AI 循环调用主脚本）

功能：Lint 静态检查 → Debug 编译 → 自动选设备部署运行 → 导出结构化日志

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 1 ]; then
    echo "用法：$0 项目根目录"
    exit 1
fi

PROJECT_ROOT=$1

echo "===== 进入自动化构建运行流水线：${PROJECT_ROOT} ====="

# 1. 静态代码校验，输出JSON报错
echo "[STEP 1] ArkTS Lint 语法校验"
devecocli lint \
  --project "${PROJECT_ROOT}" \
  --json > lint_result.json

# 判断lint是否报错
LINT_RET=$?
if [ ${LINT_RET} -ne 0 ]; then
  echo "[WARN] Lint检测到代码错误，输出 lint_result.json 供AI修复"
else
  echo "[OK] 代码静态校验无错误"
fi

# 2. 获取设备列表，自动选择首个设备ID
echo "[STEP 2] 枚举在线设备"
DEVICE_LIST=$(devecocli device list --json)
TARGET_DEVICE=$(echo ${DEVICE_LIST} | jq -r '.[0].id')

if [ "${AUTO_DEVICE}" = true ] && [ "${TARGET_DEVICE}" != "null" ]; then
  DEVICE_ARG="--device ${TARGET_DEVICE}"
  echo "自动选用设备：${TARGET_DEVICE}"
else
  echo "[ERROR] 未检测到真机/模拟器"
  exit 1
fi

# 3. Debug 编译构建
echo "[STEP 3] 增量编译Debug包"
devecocli build \
  --project "${PROJECT_ROOT}" \
  --mode debug \
  --incremental \
  --sign "${SIGN_CONFIG}"

BUILD_RET=$?
if [ ${BUILD_RET} -ne 0 ]; then
  echo "[ERROR] 编译构建失败，终止流程"
  exit 1
fi

# 4. 一键安装并启动应用
echo "[STEP 4] 部署并启动应用"
devecocli run \
  --project "${PROJECT_ROOT}" \
  ${DEVICE_ARG} \
  --sign "${SIGN_CONFIG}"

RUN_RET=$?
if [ ${RUN_RET} -ne 0 ]; then
  echo "[ERROR] 应用部署启动失败"
  exit 1
fi

# 5. 抓取应用运行日志，JSON格式输出
echo "[STEP 5] 抓取应用实时日志至 ${LOG_OUT}"
devecocli log \
  --filter "${APP_BUNDLE}" \
  --json \
  --once > ${LOG_OUT}

echo "===== 流水线执行完成 ====="
echo "静态检查结果：lint_result.json"
echo "运行日志文件：${LOG_OUT}"
exit 0
```

### 使用示例

```bash
chmod +x hm_auto_build_run.sh
./hm_auto_build_run.sh ./AutoTodoApp
```

---

## 3. hm_auto_release_package.sh 正式打包脚本

输出可分发 Release HAP 包，自动读取签名

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 1 ]; then
    echo "用法：$0 项目根目录"
    exit 1
fi

PROJECT_ROOT=$1

echo "===== 构建Release正式安装包 ====="
mkdir -p ${DIST_DIR}

devecocli build \
  --project "${PROJECT_ROOT}" \
  --mode release \
  --sign "${SIGN_CONFIG}" \
  --output ${DIST_DIR}

if [ $? -eq 0 ]; then
  echo "[SUCCESS] Release打包完成，产物目录：${DIST_DIR}"
else
  echo "[ERROR] Release打包失败"
  exit 1
fi
```

### 使用示例

```bash
chmod +x hm_auto_release_package.sh
./hm_auto_release_package.sh ./AutoTodoApp
```

---

# AI 全自动循环调用逻辑（伪代码，可嵌入你的 Agent）

```plaintext
while True:
    # AI生成/修改代码写入工程目录
    ai_generate_code()

    # 调用自动化流水线脚本
    ./hm_auto_build_run.sh ./AutoTodoApp

    # 读取结构化报错与日志
    lint_err = read_json("lint_result.json")
    runtime_log = read_json("runtime_log.json")

    # AI判断是否存在崩溃/语法错误
    if has_error(lint_err) or has_crash(runtime_log):
        ai_fix_code(lint_err, runtime_log)
        continue
    else:
        break
# 无报错后打包发布
./hm_auto_release_package.sh ./AutoTodoApp
```

# 配套 sign_config.json 调试签名模板

提前在本地导出调试证书，填入路径即可免 IDE 弹窗

```json
{
  "keyStorePath": "./debug.ks",
  "keyStorePassword": "你的密码",
  "keyAlias": "debugkey",
  "keyPassword": "你的密码"
}
```

# 依赖安装说明

1. 安装 jq：用于解析 CLI 输出的 JSON ```bash
   # mac
   brew install jq
   # linux
   apt install jq
   ```
2. 全局安装 DevEco CLI ```bash
   npm install -g @deveco/deveco-cli
   ```
3. 预先启动模拟器（可选，脚本也可扩展自动启停模拟器命令） ```bash
   devecocli emulator start --device-type phone
   ```

需要我补充一段**模拟器后台自动启停**的扩展函数，合并进构建脚本，实现完全不用手动打开模拟器吗？

---

# 4、模拟器自动启停整合流水线

---

# 升级整合版：带模拟器自动启停的完整自动化流水线脚本

## 新增能力

1. 自动检测模拟器是否运行，未运行则后台静默拉起
2. 构建结束可选择自动关闭模拟器（可选参数控制）
3. 合并模拟器逻辑到 `hm_auto_build_run.sh`，无需额外脚本
4. 增加模拟器镜像检测、静默下载提示（可扩展自动下载命令）
5. 兼容真机优先逻辑：有真机就不用模拟器，# 1、config.env 模拟器配置项更新

## 1、更新后的 config.env（新增模拟器配置项）

```env
# config.env
# 鸿蒙SDK根目录
SDK_PATH="/Users/xxx/Library/Huawei/Sdk"
# 调试签名配置文件路径
SIGN_CONFIG="./sign_config.json"
# 应用包名
APP_BUNDLE="com.example.autoapp"
# 日志输出文件
LOG_OUT="./runtime_log.json"
# 构建产物目录
DIST_DIR="./dist"

# 模拟器配置
EMU_DEVICE_TYPE="phone"
EMU_OS_VERSION="HarmonyOS 6.0.1(21)"
# 构建完成后是否自动关闭模拟器 true/false
EMU_AUTO_SHUTDOWN=false
# 真机优先：true 有真机就不用模拟器
PRIOR_PHONE=true
# 2、hm_auto_build_run.sh 模拟器逻辑增强版

## 2、新版 hm_auto_build_run.sh（内置模拟器自动启停逻辑）

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 1 ]; then
    echo "用法：$0 项目根目录"
    exit 1
fi

PROJECT_ROOT=$1

# ====================== 内部函数：模拟器管理 ======================
start_emulator() {
    echo "[EMU] 未检测到可用设备，自动启动${EMU_DEVICE_TYPE}模拟器"
    # 后台启动模拟器，无GUI弹窗阻塞
    devecocli emulator start \
        --device-type "${EMU_DEVICE_TYPE}" \
        --os-version "${EMU_OS_VERSION}" &
    EMU_PID=$!
    echo "[EMU] 模拟器后台进程PID: ${EMU_PID}"
    # 等待模拟器初始化完成
    echo "[EMU] 等待模拟器就绪，延时12s..."
    sleep 12
}

stop_emulator() {
    echo "[EMU] 执行模拟器关闭"
    devecocli emulator stop \
        --device-type "${EMU_DEVICE_TYPE}" \
        --os-version "${EMU_OS_VERSION}"
}

# ====================== 步骤1：获取设备列表、自动处理模拟器 ======================
echo "===== 设备检测阶段 ====="
DEVICE_LIST=$(devecocli device list --json)
# 提取第一个设备ID
TARGET_DEVICE=$(echo ${DEVICE_LIST} | jq -r '.[0].id')
DEVICE_COUNT=$(echo ${DEVICE_LIST} | jq 'length')

if [ "${PRIOR_PHONE}" = true ] && [ "${DEVICE_COUNT}" -gt 0 ] && [ "${TARGET_DEVICE}" != "null" ]; then
    DEVICE_ARG="--device ${TARGET_DEVICE}"
    echo "[DEVICE] 检测到在线设备 ID: ${TARGET_DEVICE}，直接使用"
else
    # 无设备，自动拉起模拟器
    start_emulator
    # 重新拉取设备列表获取模拟器ID
    DEVICE_LIST=$(devecocli device list --json)
    TARGET_DEVICE=$(echo ${DEVICE_LIST} | jq -r '.[0].id')
    DEVICE_ARG="--device ${TARGET_DEVICE}"
    echo "[DEVICE] 使用模拟器设备 ID: ${TARGET_DEVICE}"
fi

# ====================== 步骤2：Lint静态代码校验 ======================
echo -e "\n===== STEP1 ArkTS Lint 语法校验 ====="
devecocli lint \
    --project "${PROJECT_ROOT}" \
    --json > lint_result.json

LINT_RET=$?
if [ ${LINT_RET} -ne 0 ]; then
  echo "[WARN] Lint检测代码错误，结果输出至 lint_result.json"
else
  echo "[OK] 静态校验无错误"
fi

# ====================== 步骤3：Debug增量编译 ======================
echo -e "\n===== STEP2 增量编译Debug包 ====="
devecocli build \
  --project "${PROJECT_ROOT}" \
  --mode debug \
  --incremental \
  --sign "${SIGN_CONFIG}"

BUILD_RET=$?
if [ ${BUILD_RET} -ne 0 ]; then
  echo "[ERROR] 编译失败，终止流水线"
  exit 1
fi

# ====================== 步骤4：部署并启动应用 ======================
echo -e "\n===== STEP3 安装并启动应用 ====="
devecocli run \
  --project "${PROJECT_ROOT}" \
  ${DEVICE_ARG} \
  --sign "${SIGN_CONFIG}"

RUN_RET=$?
if [ ${RUN_RET} -ne 0 ]; then
  echo "[ERROR] 应用部署/启动失败"
  exit 1
fi

# ====================== 步骤5：抓取结构化运行日志 ======================
echo -e "\n===== STEP4 采集应用运行日志 ====="
devecocli log \
  --filter "${APP_BUNDLE}" \
  --json \
  --once > ${LOG_OUT}

echo "日志输出文件：${LOG_OUT}"

# ====================== 可选：流程结束自动关闭模拟器 ======================
if [ "${EMU_AUTO_SHUTDOWN}" = true ]; then
  echo -e "\n===== STEP5 自动关闭模拟器 ====="
  stop_emulator
fi

echo -e "\n===== 自动化流水线全部执行完成 ====="
echo "静态检查报告：lint_result.json"
echo "运行日志报告：${LOG_OUT}"
exit 0
`# 3、hm_auto_init.sh 与 hm_auto_release_package.sh 保持不变

## 3、原有脚本不变（hm_auto_init.sh/hm_auto_release_package.sh）

### hm_auto_init.sh

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 2 ]; then
    echo "用法：$0 项目名称 模板名"
    echo "模板可选：empty-ability / har / library"
    exit 1
fi

PROJECT_NAME=$1
TEMPLATE=$2

echo "===== 自动创建鸿蒙工程：${PROJECT_NAME} ====="
devecocli create "${PROJECT_NAME}" \
  --app-name "${APP_BUNDLE}" \
  --template "${TEMPLATE}" \
  --sdk-path "${SDK_PATH}"

if [ $? -eq 0 ]; then
  echo "[SUCCESS] 项目创建完成，目录：./${PROJECT_NAME}"
else
  echo "[ERROR] 项目创建失败"
  exit 1
fi
```

### hm_auto_release_package.sh

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 1 ]; then
    echo "用法：$0 项目根目录"
    exit 1
fi

PROJECT_ROOT=$1

echo "===== 构建Release正式安装包 ====="
mkdir -p ${DIST_DIR}

devecocli build \
  --project "${PROJECT_ROOT}" \
  --mode release \
  --sign "${SIGN_CONFIG}" \
  --output ${DIST_DIR}

if [ $? -eq 0 ]; then
  echo "[SUCCESS] Release打包完成，产物目录：${DIST_DIR}"
else
  echo "[ERROR] Release打包失败"
  exit 1
fi
```

## 4、sign_config.json 签名配置文件

```json
{
  "keyStorePath": "./debug.ks",
  "keyStorePassword": "你的证书密码",
  "keyAlias": "debugkey",
  "keyPassword": "你的密钥密码"
}
```

## 5、鸿蒙 CLI 自动化开发完整使用流程

```bash
# 1. 赋予脚本执行权限
chmod +x *.sh

# 2. AI初始化项目（仅第一次）
./hm_auto_init.sh AiTodoApp empty-ability

# 3. 全自动流水线：设备/模拟器自动管理、编译、运行、输出日志
./hm_auto_build_run.sh ./AiTodoApp

# 4. AI迭代修复代码后，再次执行上一行脚本循环验证
# 5. 功能验收无误后打包正式包
./hm_auto_release_package.sh ./AiTodoApp
```

## 6、AI Agent 鸿蒙开发自迭代执行逻辑

```python
import json
import subprocess

def run_pipeline(project_path):
    # 执行自动化shell脚本
    ret = subprocess.run(["./hm_auto_build_run.sh", project_path])
    # 读取静态报错
    with open("lint_result.json", "r", encoding="utf-8") as f:
        lint_err = json.load(f)
    # 读取运行崩溃日志
    with open("runtime_log.json", "r", encoding="utf-8") as f:
        runtime_log = json.load(f)
    return lint_err, runtime_log

# AI自迭代循环
project_dir = "./AiTodoApp"
max_loop = 8  # 限制最大修复轮次，防止死循环
loop_count = 0

while loop_count < max_loop:
    lint_errors, crash_logs = run_pipeline(project_dir)
    # AI判断是否存在语法错误、运行崩溃
    if has_errors(lint_errors) or has_crash(crash_logs):
        ai_auto_fix_code(lint_errors, crash_logs, project_dir)
        loop_count += 1
        continue
    else:
        print("代码无语法错误，运行无崩溃，迭代完成")
        break

# 打包Release产物
subprocess.run(["./hm_auto_release_package.sh", project_dir])
```

## 7、DevEco CLI 环境依赖与扩展说明

1. jq 解析 JSON 输出（必须）

```bash
# Mac
brew install jq
# Ubuntu/Debian
sudo apt update && sudo apt install jq
```

2. 全局 DevEco CLI

```bash
npm install -g @deveco/deveco-cli
```

3. 进阶扩展（可选，你可按需加进脚本）

- `devecocli emulator image download` 自动下载缺失模拟器镜像
- 增加日志错误关键词过滤（闪退、Exception、ArkUI 渲染异常）单独输出给 AI
- 增加 HSP 共享模块批量编译逻辑

---

# 5# 5、Android/iOS CLI 工具对比与成熟度分析

**问题详情：**

多问一句，android 和 ios 平台的 APP 开发，是否也有类似的 CLI 模式工具？ 与鸿蒙的这款相比，应用成熟度如何？

---

# Android /iOS 对应 CLI 工具完整对比 + 和 DevEco CLI 成熟度、AI 自动化适配分析

## 总览结论

1. **Android**：两套体系
   - 传统：`gradle + adb + sdkmanager`（十年成熟，CI 工业级，但命令碎片化，不原生适配 AI Agent）
   - 2026 新官方统一工具：**Android CLI**（Google I/O 2026 发布，对标 DevEco CLI，专为 AI 自动化设计，一体化单工具）
2. **iOS**：无苹果官方一体化 CLI，分为两层
   - 底层原生：`xcodebuild + xcrun + simctl`（系统自带，功能零散、参数复杂、交互弹窗多）
   - 社区成熟封装：**Fastlane**（行业事实标准，Ruby 生态，自动化极强，但第三方工具，非苹果官方）
3. **DevEco CLI**：华为原生一体化单工具，**从设计之初面向 AI Agent 本地全自动闭环**；发布时间最晚，但 AI 原生适配理念领先 Android/iOS 传统工具。

## 一、Android 端 CLI 工具详解

### 1. 传统组合：Gradle + ADB + sdkmanager（成熟度极高，2014 至今）

#### 分工

- gradlew：项目构建、打包 APK/AAB、代码 Lint、单元测试
- adb：设备 / 模拟器安装应用、启动页面、抓取 logcat 日志
- sdkmanager/avdmanager：SDK 下载、模拟器创建 / 启停

#### 自动化痛点（对比 DevEco CLI）

1. **工具割裂**：三套独立命令，无统一入口，AI 需要维护多套调用逻辑；没有类似`devecocli run`一键「构建 + 安装 + 启动」，必须脚本拼接多段指令
2. 输出文本无标准化 JSON：日志、报错原始文本杂乱，AI 解析成本极高
3. 无内置项目脚手架统一命令、无官方知识库查询、无 MCP AI 协议支持
4. 模拟器管理繁琐，启停、等待就绪需要手动 sleep 硬编码

#### 成熟度：★★★★★（工业 CI 流水线全球普及，稳定性拉满）

### 2. 全新官方一体化：Android CLI（2026 Google I/O 发布，对标 DevEco CLI）

Google 专门为 AI 编程 Agent 推出的**单一统一命令行工具**，定位、设计思路完全对齐 DevEco CLI：

- 统一入口 `android`，整合项目创建、构建、模拟器、部署、日志、Lint、SDK 管理
- 全部命令支持`--json`结构化输出，内置 MCP 协议对接本地 AI 工具
- 单命令`android run` = 编译 + 安装 + 启动应用，自动选择设备 / 拉起模拟器
- 内置官方安卓 API 知识库查询、Compose UI 预览生成

#### 成熟度：★★★☆☆（刚发布，基础能力齐全，但生态插件、社区案例少）

## 二、iOS 端 CLI 工具详解（无官方一体化单工具）

### 1. 苹果原生底层：xcodebuild + simctl + xcrun（系统自带）

- xcodebuild：编译、归档、导出 IPA 包，打包签名
- simctl：模拟器创建、启停、截图、安装 App
- xcrun：配套工具链调用、设备管理

#### 核心短板

1. 参数极其冗长复杂，一条打包命令几十行参数，极易出错
2. 签名流程强制依赖苹果开发者账号，自动化时频繁弹窗 2FA、证书弹窗，很难无人值守
3. 无统一日志过滤工具，日志输出混乱，无结构化 JSON
4. 只能运行在 macOS，Windows/Linux 完全不支持

#### 成熟度：★★★★☆（底层能力完整，但原生 CLI 极不适合本地 AI 全自动闭环）

### 2. 社区封装王者：Fastlane（Ruby 开发，全球 iOS 自动化标准）

行业几乎所有 iOS CI / 本地自动化都用它，对原生命令做高层封装：

- 封装`gym`打包、`scan`自动化测试、`snapshot`截图、`pilot`上传 TestFlight
- 统一配置文件 Fastfile，单条指令完成全流程，自动处理证书、2FA、模拟器
- 支持 JSON 结构化输出，可嵌入脚本循环调用

#### 关键局限（对比 DevEco CLI）

1. **第三方工具，非苹果官方**：Xcode 大版本更新经常出现兼容崩溃，需要等社区修复
2. 依赖 Ruby 环境，额外一层运行时，本地 AI 环境部署更重
3. 缺少**代码生成 / 脚手架 / 官方文档检索**这类 AI 编程配套能力，只做构建发布自动化
4. 无原生 MCP 协议对接本地 AI Agent，需要自行封装桥接层

#### 成熟度：★★★★★（十年社区沉淀，企业级 iOS 自动化首选）

## 三、四大工具横向对比（DevEco CLI / Android 传统工具 / Android 新 CLI / Fastlane (iOS)）

| 对⁠比⁠维⁠度 | DevEco CLI（鸿⁠蒙） | Android 传⁠统 Gradle+ADB | Android CLI（2026 新⁠官⁠方） | Fastlane(iOS) |
| --- | --- | --- | --- | --- |
| **官⁠方⁠归⁠属** | 华⁠为⁠原⁠生⁠一⁠体⁠化⁠单⁠工⁠具 | Google 原⁠生⁠多⁠工⁠具⁠组⁠合 | Google 官⁠方⁠一⁠体⁠化⁠单⁠工⁠具 | 第⁠三⁠方⁠社⁠区⁠开⁠源 |
| **设⁠计⁠初⁠衷** | AI Agent 全⁠自⁠动⁠本⁠地⁠编⁠程⁠闭⁠环 | CI 服⁠务⁠端⁠批⁠量⁠打⁠包 | AI Agent 本⁠地⁠自⁠动⁠化，对⁠标 DevEco CLI | 流⁠水⁠线⁠打⁠包、测⁠试、上⁠架 |
| **统⁠一⁠单⁠入⁠口** | ✅ 全⁠部⁠功⁠能⁠一⁠条`devecocli` | ❌ gradlew/adb/sdkmanager 多⁠命⁠令 | ✅ 统⁠一`android`命⁠令 | ✅ 统⁠一`fastlane`，底⁠层⁠封⁠装 xcodebuild |
| 一⁠键 run（构⁠建 + 安⁠装 + 启⁠动） | ✅ 原⁠生⁠支⁠持 | ❌ 需⁠要⁠脚⁠本⁠拼⁠接⁠多⁠命⁠令 | ✅ 原⁠生`android run` | ❌ 需⁠要⁠组⁠合 gym+install 命⁠令 |
| JSON 结⁠构⁠化⁠输⁠出 | ✅ 全⁠命⁠令⁠内⁠置`--json` | ❌ 原⁠生⁠无，需 awk/grep 解⁠析 | ✅ 全⁠命⁠令 JSON 输⁠出 | ✅ 支⁠持⁠配⁠置⁠输⁠出 JSON 报⁠告 |
| 模⁠拟⁠器⁠自⁠动⁠启⁠停、等⁠待⁠就⁠绪 | ✅ 内⁠置⁠封⁠装，无⁠需 sleep 硬⁠编⁠码 | ❌ 需⁠自⁠行⁠写⁠延⁠时⁠逻⁠辑 | ✅ 原⁠生⁠模⁠拟⁠器⁠管⁠理 | ✅ 封⁠装 simctl，自⁠动⁠等⁠待 |
| 项⁠目⁠脚⁠手⁠架⁠自⁠动⁠创⁠建 | ✅ create 命⁠令⁠原⁠生⁠支⁠持 | ❌ gradle init 简⁠陋，模⁠板⁠不⁠全 | ✅ android create 标⁠准⁠化⁠模⁠板 | ❌ 仅⁠构⁠建，无⁠项⁠目⁠生⁠成 |
| 代⁠码 Lint 静⁠态⁠校⁠验 | ✅ 内⁠置⁠统⁠一⁠命⁠令 | ✅ gradle lint，但⁠输⁠出⁠杂⁠乱 | ✅ 一⁠体⁠化 lint | ❌ 需⁠单⁠独⁠调⁠用 xcode lint |
| 官⁠方 SDK/API 知⁠识⁠库⁠查⁠询 | ✅ 内⁠置 docs 命⁠令 | ❌ 无 | ✅ 内⁠置⁠文⁠档⁠检⁠索 | ❌ 无，依⁠赖⁠外⁠部⁠文⁠档 |
| MCP 协⁠议⁠对⁠接⁠本⁠地 AI 工⁠具 | ✅ 原⁠生⁠内⁠置 agent 接⁠入 | ❌ 无，需⁠自⁠行⁠封⁠装 | ✅ 原⁠生 MCP 支⁠持 | ❌ 无，需⁠自⁠行⁠封⁠装⁠桥⁠接 |
| 跨⁠操⁠作⁠系⁠统 | Windows/macOS/Linux 全⁠支⁠持 | 全⁠平⁠台 | 全⁠平⁠台 | 仅 macOS 可⁠用 |
| 无⁠人⁠值⁠守⁠免⁠弹⁠窗⁠签⁠名 | ✅ 读⁠取⁠本⁠地 json 签⁠名⁠配⁠置，无⁠登⁠录⁠弹⁠窗 | ✅ gradle 配⁠置⁠签⁠名⁠文⁠件 | ✅ 本⁠地⁠配⁠置⁠签⁠名 | 可⁠自⁠动⁠处⁠理⁠证⁠书，但⁠苹⁠果 2FA 仍⁠有⁠卡⁠点 |
| 发⁠布⁠时⁠间 & 成⁠熟⁠度 | 2026 HDC 发⁠布，新⁠工⁠具；AI 适⁠配⁠成⁠熟，生⁠态⁠待⁠扩⁠充 | 2014 至⁠今，工⁠业⁠级⁠极⁠度⁠成⁠熟 | 2026 I/O 刚⁠发⁠布，基⁠础⁠稳⁠定、生⁠态⁠少 | 2015 至⁠今，iOS 自⁠动⁠化⁠事⁠实⁠标⁠准 |

## 四、分平台：纯本地 AI 全自动开发可行性（你的需求：AI 全权编码，人仅验收反馈）

### 1. 鸿蒙 DevEco CLI

**最贴合你的深度 AI 编程场景**

- 原生为 Agent 设计，一条脚本完成「创建项目→代码校验→编译→自动设备 / 模拟器→运行→结构化日志输出」
- 无多余中间工具依赖，一套环境搞定全流程，不用处理多语言运行时（Ruby/Gradle）
- 所有输出机器可读 JSON，AI 自动解析报错循环修复，完美实现零人工 IDE 点击操作

### 2. Android 两条路线

#### 路线 A：传统 Gradle+ADB

可以实现自动化，但**脚本臃肿、维护成本高**：
 需要自行拼接十多条独立命令、写大量文本解析逻辑、手动处理模拟器等待、日志过滤，AI 调用链路复杂，容易出现兼容 bug；适合服务端 CI，不适合本地 AI 高频迭代自修复。

#### 路线 B：Android CLI（2026 新官方）

体验和 DevEco CLI 几乎持平，AI 友好度拉满，但缺点是发布时间太短，网络案例、踩坑方案极少，遇到问题很难找到解决方案。

### 3. iOS Fastlane + xcodebuild

**自动化能力最强，但有硬性短板限制本地 AI 闭环**

1. 只能在 macOS 运行，Windows/Linux 本地 AI 环境完全无法使用；
2. 苹果账号 2FA、证书配置偶尔仍会弹出人工交互弹窗，很难做到 100% 无人值守；
3. Fastlane 只负责构建打包，没有项目生成、代码智能校验、API 文档查询这类 AI 编程配套功能；
4. 依赖 Ruby 环境，本地 AI 多工具并存时容易出现环境版本冲突。

## 五、成熟度综合排序（分两个维度）

### 维度 1：企业 CI / 服务端批量打包成熟度（稳定性、生态、踩坑方案）

1. Fastlane(iOS) ★★★★★
2. Gradle+ADB (Android 传统) ★★★★★
3. DevEco CLI (鸿蒙) ★★★☆☆
4. Android CLI (2026 新) ★★☆☆☆

### 维度 2：本地 AI 全自动编程适配成熟度（单工具一体化、JSON 输出、MCP、脚手架、无人工弹窗）

1. DevEco CLI (鸿蒙) ★★★★★（原生 AI Agent 设计，最优）
2. Android CLI (2026 新官方) ★★★★☆（设计对齐鸿蒙，但生态不足）
3. Fastlane (iOS) ★★★☆☆（自动化强，但缺少 AI 编程配套，平台受限）
4. Gradle+ADB (Android 传统) ★★☆☆☆（碎片化严重，AI 解析成本极高）

## 六、针对你「深度本地 AI 编程」场景选型建议

1. **鸿蒙**：直接纯 DevEco CLI，现有整套 shell 脚本可直接复用，自动化闭环体验最优，几乎无人工介入点；
2. **Android**：短期先用 Gradle+ADB 写自动化脚本兜底，长期切换 Android CLI 简化 AI 调用逻辑；
3. **iOS**：仅 macOS 环境可用 Fastlane 做流水线，但很难做到完全脱离人工弹窗；若你是 Windows 本地 AI 开发，iOS 全自动化 CLI 几乎无解。

## 补充：三者自动化脚本开发差异小结

- 鸿蒙：一套 shell 脚本，单一`devecocli`命令集，逻辑极简，AI 循环修复代码链路最短；
- Android 传统：脚本需要混合 gradlew、adb、avdmanager、sdkmanager 四类命令，大量文本处理；
- iOS Fastlane：需要同时维护 Ruby Fastfile + Shell 两层逻辑，额外处理苹果签名、设# 6、DevEco CLI 全生命周期开发教程

---

# 6、提供一份使用 DevEco C...

**问题详情：**

提供一份使用 DevEco CLI 进行鸿蒙 APP 开发的教程

---

# DevEco CLI 鸿蒙全命令行开发完整教程（脱离 DevEco IDE、适配 AI 全自动编程）

## 教程总览

本教程全程**不打开 DevEco Studio 图形界面**，仅用终端 + DevEco CLI 完成鸿蒙 App 全生命周期：环境安装→签名配置→创建项目→编码校验→模拟器 / 真机自动管理→编译运行→日志采集→Release 打包→对接 AI Agent 自动化闭环。
 适配 Windows/macOS/Linux，配套前文 Shell 流水线脚本，适合深度 AI 本地编程场景。

![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%27256%27%20height=%27192%27/%3e)![image](https://p26-flow-imagex-sign.byteimg.com/labis/image/6fc6914924ce3f90d36f045e78b64c76~tplv-a9rns2rl98-pc_smart_face_crop-v1:512:384.image?lk3s=8e244e95&rcl=20260716144308C5B0251649F91A4739D2&rrcfp=cee388b0&x-expires=2099544198&x-signature=PF7CbPLJLyJMqCE%2FZg3wj8Nt5Pw%3D)

# 一、前置环境要求

## 1. 必备软件

1. Node.js ≥ 18（推荐 22 LTS），自带 npm
2. JDK 17（鸿蒙官方编译要求）
3. DevEco Studio ≥ 6.1.0（仅用于提供 SDK、模拟器镜像，无需打开 GUI）
4. Windows：Git Bash / WSL；macOS/Linux：原生 bash
5. 依赖解析工具 `jq`（用于读取 CLI 结构化 JSON 输出，AI 自动化必备）

## 2. 环境校验命令

```bash
# 检查Node、JDK版本
node -v
java -version
# 检查jq
jq --version
```

# 二、DevEco CLI 安装与全局配置

## 1. 全局安装 CLI 工具

```bash
# 官方包全局安装
npm install -g @deveco/deveco-cli@latest
# 验证安装成功
devecocli --version
# 更新CLI到最新版
devecocli update
```

## 2. 核心全局配置（一次性操作）

### 2.1 配置鸿蒙 SDK 路径

CLI 需要读取 DevEco Studio 内置 SDK，否则编译失败：

```bash
# macOS示例
devecocli config set sdk.path "/Applications/DevEco Studio.app/Contents/sdk"
# Windows示例
devecocli config set sdk.path "C:\Huawei\DevEco Studio\sdk"
# 查看当前所有配置
devecocli config list
```

### 2.2 模拟器许可协议（首次运行必须）

```bash
devecocli emulator license accept
```

# 三、调试签名文件生成（全自动打包无弹窗关键）

IDE 手动导出调试证书，CLI 读取 JSON 配置免账号登录、免弹窗。

## 步骤 1：DevEco Studio 一次性生成调试密钥

1. 打开 DevEco Studio（仅这一步需要 GUI）
2. File → Project Structure → Signing Configs
3. 勾选 `Automatically generate signature`，导出 `debug.ks` 密钥文件，记录密码、别名
4. 将 `debug.ks` 复制到脚本目录

## 步骤 2：创建签名配置 `sign_config.json`

```json
{
  "keyStorePath": "./debug.ks",
  "keyStorePassword": "你的密钥库密码",
  "keyAlias": "debugkey",
  "keyPassword": "你的密钥密码"
}
```

# 四、核心命令全解（分模块，可直接被 AI 调用）

## 1. 项目脚手架 create（新建应用 / 共享模块）

### 基础语法

```bash
devecocli create 项目名 [参数]
```

### 常用参数

- `--app-name`：应用唯一包名（如`com.example.aihmapp`）
- `--template`：项目模板
  - `empty-ability`：空白 ArkTS 应用（日常开发首选）
  - `har`：共享静态库模块
  - `library`：C/C++ 原生库
- `--api-level`：目标 API 版本（26=HarmonyOS7）

### 示例：创建空白鸿蒙应用

```bash
devecocli create AiTodoApp \
--app-name com.example.aitodo \
--template empty-ability \
--api-level 26
```

## 2. 代码静态校验 lint（AI 自动修复前置）

输出结构化 JSON 报错，机器可读，无需人工阅读控制台：

```bash
# 全项目校验，结果输出JSON文件
devecocli lint --project ./AiTodoApp --json > lint_error.json
```

## 3. 编译构建 build（Debug/Release 双模式）

### Debug 增量编译（开发调试）

```bash
devecocli build \
--project ./AiTodoApp \
--mode debug \
--incremental \
--sign ./sign_config.json
```

### Release 正式打包（上架分发）

```bash
devecocli build \
--project ./AiTodoApp \
--mode release \
--sign ./sign_config.json \
--output ./dist/release
```

## 4. 设备管理 device（真机 / 模拟器统一查询）

```bash
# 列出所有在线设备（真机+运行中模拟器）
devecocli device list --json
# 查看指定设备详细信息
devecocli device view --target 设备ID
```

## 5. 模拟器全生命周期管理（自动启停核心）

```bash
# 查看本地已下载模拟器镜像
devecocli emulator list
# 下载手机模拟器镜像
devecocli emulator image download \
--device-type phone \
--os-version "HarmonyOS 7.0.0(26)"
# 后台静默启动模拟器
devecocli emulator start \
--device-type phone \
--os-version "HarmonyOS 7.0.0(26)"
# 关闭模拟器
devecocli emulator stop --device-type phone
```

## 6. 一键部署运行 run（替代 IDE 点击 Run 按钮）

单命令：编译 + 签名 + 安装应用 + 启动 Ability，支持自动选设备

```bash
devecocli run \
--project ./AiTodoApp \
--sign ./sign_config.json \
--auto-select-device
```

`--auto-select-device`：自动选用第一个可用设备，无需人工下拉选择

## 7. 日志采集 log（AI 自动定位崩溃、业务异常）

支持 JSON 结构化输出、崩溃过滤、实时追踪：

```bash
# 一次性抓取应用全部日志，输出JSON
devecocli log \
--filter com.example.aitodo \
--json --once > runtime_log.json

# 实时跟踪日志，仅打印Error崩溃日志
devecocli log --filter com.example.aitodo --level E --follow
```

## 8. 配套辅助命令

```bash
# 本地鸿蒙官方文档检索（AI写代码查API专用）
devecocli docs search ArkUI List
# 挂载MCP协议，对接Cursor/Claude Code等AI工具
devecocli init --agent local-ai
# 三方依赖ohpm统一管理（等同于npm）
devecocli ohpm install @ohos/sqlite
```

# 五、完整手工开发流程（纯终端，零 IDE 点击）

## 阶段 1：初始化项目

```bash
# 1. 创建项目
devecocli create AiTodoApp --app-name com.example.aitodo --template empty-ability
cd AiTodoApp
# 2. VSCode打开项目编写ArkTS代码（仅编辑器，无IDE图形工具）
code .
```

## 阶段 2：静态代码校验

```bash
devecocli lint --project ./AiTodoApp --json > lint_result.json
# 打开lint_result.json查看语法、类型报错
```

## 阶段 3：启动模拟器（无真机时）

```bash
# 后台拉起模拟器，等待12秒初始化完成
devecocli emulator start --device-type phone --os-version "HarmonyOS 7.0.0(26)"
sleep 12
```

## 阶段 4：一键编译、安装、启动 App

```bash
devecocli run --project ./AiTodoApp --sign ../sign_config.json --auto-select-device
```

## 阶段 5：抓取运行日志排查问题

```bash
devecocli log --filter com.example.aitodo --json --once > runtime_log.json
```

## 阶段 6：验证无误后打包 Release 安装包

```bash
devecocli build --project ./AiTodoApp --mode release --sign ../sign_config.json --output ../dist
```

# 六、全自动 Shell 流水线集成（AI 编程专用，前文完整脚本）

## 配套文件清单

1. `config.env` 全局环境配置
2. `hm_auto_init.sh` 自动创建项目
3. `hm_auto_build_run.sh` 核心流水线（模拟器自动启停 + lint+build+run + 日志输出）
4. `hm_auto_release_package.sh` 正式打包脚本
5. `sign_config.json` 签名配置

## 一键自动化完整链路

```bash
# 1. 赋予脚本执行权限
chmod +x *.sh
# 2. AI初始化新项目（仅首次）
./hm_auto_init.sh AiTodoApp empty-ability
# 3. 全自动闭环：设备/模拟器自动管理、校验、编译、运行、导出日志
./hm_auto_build_run.sh ./AiTodoApp
# 4. 功能验收后打包发布包
./hm_auto_release_package.sh ./AiTodoApp
```

## AI 自迭代循环逻辑（Python 示例，嵌入本地 AI 工具）

```python
import subprocess, json

def auto_harmony_pipeline(project_dir):
    # 执行CLI自动化shell脚本
    subprocess.run(["./hm_auto_build_run.sh", project_dir])
    # 读取结构化报错与运行日志
    with open("lint_result.json","r",encoding="utf-8") as f:
        lint_errors = json.load(f)
    with open("runtime_log.json","r",encoding="utf-8") as f:
        crash_logs = json.load(f)
    return lint_errors, crash_logs

# AI循环修复，最多8轮防止死循环
max_loop = 8
loop = 0
project = "./AiTodoApp"

while loop < max_loop:
    errs, logs = auto_harmony_pipeline(project)
    # AI判断是否存在语法错误/运行崩溃
    if has_error(errs) or has_crash(logs):
        ai_fix_code(errs, logs, project)
        loop += 1
        continue
    break
# 无错误自动打包Release
subprocess.run(["./hm_auto_release_package.sh", project])
```

# 七、DevEco CLI 与 DevEco Code 协作关系（AI 开发架构）

1. **DevEco Code（AI 大脑）**：接收自然语言需求、生成 ArkTS 代码、解析 JSON 报错、自动修复逻辑、生成测试用例；
2. **DevEco CLI（执行终端）**：提供标准化原子命令，负责项目创建、编译、真机 / 模拟器调度、日志采集、打包；
3. 完整自动化链路：`用户需求 → DevEco Code生成代码 → CLI lint校验 → CLI build编译 → CLI run部署 → CLI log返回日志 → DevEco Code自动修复代码（循环）`

全程无需人工点击 IDE 按钮，仅需人工打开设备 App 验收功能并反馈问题。

# 八、常见问题与避坑指南

1. **SDK 路径配置错误，编译失败** 执行 `devecocli config set sdk.path` 重新指定 DevEco Studio 的 sdk 目录；
2. **模拟器启动超时** 脚本内置 sleep 延时可调整至 15s，提前下载对应系统镜像；
3. **签名弹窗、打包失败** 确保`sign_config.json`密钥路径、密码、别名与导出的 ks 文件完全匹配；
4. **JSON 输出为空，AI 无法解析报错** 所有命令必须添加`--json`参数，安装`jq`工具；
5. **真机无法识别** 手机开启 USB 调试，首次手动允许授权，后续 CLI 自动识别；
6. **Windows 终端报错** 不要使用原生 CMD，切换 Git Bash/WSL 执行 Shell 脚本。

# 九、跨平台对比补充（Android/iOS CLI 对比回顾）

1. **鸿蒙 DevEco CLI**：原生一体化单工具，从底层面向 AI 自动化设计，JSON 输出、MCP 协议、模拟器封装完善，本地 AI 编程最优；
2. **Android 传统 Gradle+ADB**：工具碎片化，脚本臃肿，无原生 AI 适配；新版 Android CLI 设计对齐鸿蒙，但生态不成熟；
3. **iOS Fastlane**：第三方封装，仅 macOS 可用，证书 2FA 存在人工弹窗，缺少项目脚手架、API 检索等 AI 配套能力。

需要我把整套可直接复制的 `config.env`、三个 Shell 脚本、签名模板整合为一份完整压缩式文本，你一键复制保存即可使用吗？

---

# 7、DevEco CLI 自动化脚本压缩包合集

---

# 全套 DevEco CLI 自动化开发文件 一键复制合集

## 目录结构

```plaintext
hm-auto-cli/
├── config.env               # 全局环境配置
├── sign_config.json         # 调试签名配置
├── hm_auto_init.sh          # 新建项目脚本
├── hm_auto_build_run.sh     # 核心流水线（模拟器自动启停+lint+build+run+日志）
├── hm_auto_release_package.sh # Release打包脚本
```

---

## 1. config.env

```env
# ====================== DevEco CLI 全局环境配置 ======================
# 鸿蒙SDK路径，根据自己系统修改
# macOS 示例: SDK_PATH="/Applications/DevEco Studio.app/Contents/sdk"
# Windows WSL/GitBash 示例: SDK_PATH="/c/Huawei/DevEco Studio/sdk"
SDK_PATH="/Applications/DevEco Studio.app/Contents/sdk"

# 调试签名文件路径
SIGN_CONFIG="./sign_config.json"
# 应用默认包名，新建项目会沿用
APP_BUNDLE="com.example.aihmapp"
# 运行日志输出文件
LOG_OUT="./runtime_log.json"
# Release打包产物输出目录
DIST_DIR="./dist"

# 模拟器配置
EMU_DEVICE_TYPE="phone"
EMU_OS_VERSION="HarmonyOS 7.0.0(26)"
# 构建完成是否自动关闭模拟器 true/false
EMU_AUTO_SHUTDOWN=false
# 真机优先：检测到真机则不启动模拟器
PRIOR_PHONE=true
```

---

## 2. sign_config.json

```json
{
  "keyStorePath": "./debug.ks",
  "keyStorePassword": "替换为你的密钥库密码",
  "keyAlias": "debugkey",
  "keyPassword": "替换为你的密钥密码"
}
```

> 说明：debug.ks 需要你打开一次 DevEco Studio 图形界面导出一次，后续全程不用 IDE。

---

## 3. hm_auto_init.sh

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 2 ]; then
    echo "用法：$0 项目名称 模板名"
    echo "可选模板：empty-ability / har / library"
    exit 1
fi

PROJECT_NAME=$1
TEMPLATE=$2

echo "===== 自动创建鸿蒙工程：${PROJECT_NAME} ====="
devecocli create "${PROJECT_NAME}" \
  --app-name "${APP_BUNDLE}" \
  --template "${TEMPLATE}" \
  --sdk-path "${SDK_PATH}" \
  --api-level 26

if [ $? -eq 0 ]; then
  echo "[SUCCESS] 项目创建完成，目录：./${PROJECT_NAME}"
else
  echo "[ERROR] 项目创建失败"
  exit 1
fi
```

---

## 4. hm_auto_build_run.sh（核心流水线，内置模拟器启停）

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 1 ]; then
    echo "用法：$0 项目根目录"
    exit 1
fi

PROJECT_ROOT=$1

# ====================== 模拟器管理函数 ======================
start_emulator() {
    echo "[EMU] 未检测到可用设备，自动启动${EMU_DEVICE_TYPE}模拟器"
    devecocli emulator start \
        --device-type "${EMU_DEVICE_TYPE}" \
        --os-version "${EMU_OS_VERSION}" &
    EMU_PID=$!
    echo "[EMU] 模拟器后台进程PID: ${EMU_PID}"
    echo "[EMU] 等待模拟器初始化15s..."
    sleep 15
}

stop_emulator() {
    echo "[EMU] 关闭模拟器"
    devecocli emulator stop \
        --device-type "${EMU_DEVICE_TYPE}" \
        --os-version "${EMU_OS_VERSION}"
}

# ====================== 设备自动检测逻辑 ======================
echo "===== 设备检测阶段 ====="
DEVICE_LIST=$(devecocli device list --json)
TARGET_DEVICE=$(echo ${DEVICE_LIST} | jq -r '.[0].id')
DEVICE_COUNT=$(echo ${DEVICE_LIST} | jq 'length')

if [ "${PRIOR_PHONE}" = true ] && [ "${DEVICE_COUNT}" -gt 0 ] && [ "${TARGET_DEVICE}" != "null" ]; then
    DEVICE_ARG="--device ${TARGET_DEVICE}"
    echo "[DEVICE] 检测到在线设备 ID: ${TARGET_DEVICE}"
else
    start_emulator
    DEVICE_LIST=$(devecocli device list --json)
    TARGET_DEVICE=$(echo ${DEVICE_LIST} | jq -r '.[0].id')
    DEVICE_ARG="--device ${TARGET_DEVICE}"
    echo "[DEVICE] 使用模拟器设备 ID: ${TARGET_DEVICE}"
fi

# ====================== STEP1 ArkTS Lint 静态校验 ======================
echo -e "\n===== STEP1 代码静态检查 ====="
devecocli lint \
    --project "${PROJECT_ROOT}" \
    --json > lint_result.json

LINT_RET=$?
if [ ${LINT_RET} -ne 0 ]; then
  echo "[WARN] Lint存在代码错误，输出至 lint_result.json"
else
  echo "[OK] 静态校验无错误"
fi

# ====================== STEP2 Debug增量编译 ======================
echo -e "\n===== STEP2 编译Debug安装包 ====="
devecocli build \
  --project "${PROJECT_ROOT}" \
  --mode debug \
  --incremental \
  --sign "${SIGN_CONFIG}"

BUILD_RET=$?
if [ ${BUILD_RET} -ne 0 ]; then
  echo "[ERROR] 编译失败，流水线终止"
  exit 1
fi

# ====================== STEP3 安装并启动应用 ======================
echo -e "\n===== STEP3 部署并启动App ====="
devecocli run \
  --project "${PROJECT_ROOT}" \
  ${DEVICE_ARG} \
  --sign "${SIGN_CONFIG}"

RUN_RET=$?
if [ ${RUN_RET} -ne 0 ]; then
  echo "[ERROR] 应用安装/启动失败"
  exit 1
fi

# ====================== STEP4 导出结构化运行日志 ======================
echo -e "\n===== STEP4 采集应用运行日志 ====="
devecocli log \
  --filter "${APP_BUNDLE}" \
  --json \
  --once > ${LOG_OUT}
echo "运行日志文件：${LOG_OUT}"

# ====================== 可选：自动关闭模拟器 ======================
if [ "${EMU_AUTO_SHUTDOWN}" = true ]; then
  echo -e "\n===== STEP5 自动关闭模拟器 ====="
  stop_emulator
fi

echo -e "\n===== 自动化流水线执行完毕 ====="
echo "静态错误报告：lint_result.json"
echo "运行崩溃日志：${LOG_OUT}"
exit 0
```

---

## 5. hm_auto_release_package.sh

```bash
#!/bin/bash
source ./config.env

if [ $# -lt 1 ]; then
    echo "用法：$0 项目根目录"
    exit 1
fi

PROJECT_ROOT=$1

echo "===== 构建Release正式分发包 ====="
mkdir -p ${DIST_DIR}

devecocli build \
  --project "${PROJECT_ROOT}" \
  --mode release \
  --sign "${SIGN_CONFIG}" \
  --output ${DIST_DIR}

if [ $? -eq 0 ]; then
  echo "[SUCCESS] Release打包完成，产物目录：${DIST_DIR}"
else
  echo "[ERROR] Release打包失败"
  exit 1
fi
```

---

# 配套部署 & 使用说明

## 一、前置依赖安装

```bash
# 1. 安装jq（解析JSON输出，必须）
# Mac
brew install jq
# Ubuntu/Debian
sudo apt update && sudo apt install jq

# 2. 全局安装DevEco CLI
npm install -g @deveco/deveco-cli@latest

# 3. 一次性接受模拟器协议
devecocli emulator license accept
```

## 二、赋予脚本执行权限

```bash
chmod +x *.sh
```

## 三、标准使用流程

```bash
# 1. AI新建项目
./hm_auto_init.sh AiTodoApp empty-ability

# 2. 全自动流水线（模拟器自动管理、校验、编译、运行、输出日志）
./hm_auto_build_run.sh ./AiTodoApp

# 3. 验收无问题后打包正式包
./hm_auto_release_package.sh ./AiTodoApp
```

## 四、AI 循环调用伪代码（Python）

```python
import subprocess
import json

def run_harmony_flow(project_path):
    subprocess.run(["./hm_auto_build_run.sh", project_path])
    with open("lint_result.json", "r", encoding="utf-8") as f:
        lint_data = json.load(f)
    with open("runtime_log.json", "r", encoding="utf-8") as f:
        log_data = json.load(f)
    return lint_data, log_data

project = "./AiTodoApp"
max_repair_loop = 8
cur = 0

while cur < max_repair_loop:
    lint_err, crash_log = run_harmony_flow(project)
    # 此处为AI逻辑：判断是否存在语法/运行错误，自动修改代码
    if ai_has_error(lint_err, crash_log):
        ai_auto_fix(lint_err, crash_log, project)
        cur += 1
        continue
    break

# 自动打包Release
subprocess.run(["./hm_auto_release_package.sh", project])
```

## 五、Windows 用户注意

1. 不要用 CMD，使用 Git Bash / WSL2 执行脚本；
2. SDK 路径反斜杠改为 `/`；
3. debug.ks 放置在脚本同目录。

---

# 8、DevEco CLI 实操入门指南

**问题详情：**

如何使用 DevEco CLI 进行鸿蒙 APP 开发？

---

# DevEco CLI 完整实操教程（纯命令行、脱离 DevEco IDE，适配 AI 全自动开发）

## 一、环境准备（一次性配置）

### 1. 必备软件

1. Node.js ≥18 LTS（提供 npm 安装 CLI）
2. JDK 17（鸿蒙编译强制要求）
3. DevEco Studio（仅用来提供 SDK、模拟器镜像，不用打开图形界面）
4. 工具 `jq`：解析 CLI 输出的 JSON 结构化日志（AI 自动化必备）
5. 终端：macOS/Linux 原生 bash；Windows 用 Git Bash / WSL2

### 2. 安装 DevEco CLI

```bash
# 全局安装官方CLI工具
npm install -g @deveco/deveco-cli@latest
# 校验安装
devecocli --version
# 更新CLI
devecocli update
```

### 3. 全局核心配置

#### ① 绑定鸿蒙 SDK 路径

```bash
# Mac示例
devecocli config set sdk.path "/Applications/DevEco Studio.app/Contents/sdk"
# Windows WSL示例
devecocli config set sdk.path "/c/Huawei/DevEco Studio/sdk"

# 查看全部配置
devecocli config list
```

#### ② 同意模拟器协议（首次必执行）

```bash
devecocli emulator license accept
```

### 4. 生成调试签名（实现无弹窗自动打包）

1. 仅打开一次 DevEco Studio 图形界面：`File → Project Structure → Signing Configs`，自动生成调试证书 `debug.ks`，记录密钥密码、别名。
2. 将 `debug.ks` 放到脚本目录，新建`sign_config.json`：

```json
{
  "keyStorePath": "./debug.ks",
  "keyStorePassword": "你的密钥库密码",
  "keyAlias": "debugkey",
  "keyPassword": "你的密钥密码"
}
```

## 二、配套自动化脚本（直接复制使用）

### 1. config.env 全局配置文件

```env
# SDK路径，自行修改
SDK_PATH="/Applications/DevEco Studio.app/Contents/sdk"
# 签名配置文件
SIGN_CONFIG="./sign_config.json"
# 默认应用包名
APP_BUNDLE="com.example.aihmapp"
# 日志输出文件
LOG_OUT="./runtime_log.json"
# Release产物文件夹
DIST_DIR="./dist"

# 模拟器参数
EMU_DEVICE_TYPE="phone"
EMU_OS_VERSION="HarmonyOS 7.0.0(26)"
# 流水线结束是否关闭模拟器
EMU_AUTO_SHUTDOWN=false
# 有真机优先使用真机
PRIOR_PHONE=true
```

### 2. hm_auto_init.sh 创建项目脚本

```bash
#!/bin/bash
source ./config.env
if [ $# -lt 2 ]; then
    echo "用法：$0 项目名 模板名"
    echo "模板：empty-ability / har / library"
    exit 1
fi
PROJECT_NAME=$1
TEMPLATE=$2
devecocli create "${PROJECT_NAME}" \
  --app-name "${APP_BUNDLE}" \
  --template "${TEMPLATE}" \
  --sdk-path "${SDK_PATH}" \
  --api-level 26
[ $? -eq 0 ] && echo "项目创建完成 ./${PROJECT_NAME}" || echo "创建失败"
```

### 3. hm_auto_build_run.sh 核心流水线（模拟器自动启停 + 校验 + 编译 + 运行 + 日志）

```bash
#!/bin/bash
source ./config.env
if [ $# -lt 1 ]; then echo "用法：$0 项目根目录"; exit 1; fi
PROJECT_ROOT=$1

# 模拟器启停函数
start_emulator(){
    echo "无可用设备，启动模拟器"
    devecocli emulator start --device-type ${EMU_DEVICE_TYPE} --os-version ${EMU_OS_VERSION} &
    sleep 15
}
stop_emulator(){
    devecocli emulator stop --device-type ${EMU_DEVICE_TYPE} --os-version ${EMU_OS_VERSION}
}

# 自动识别真机/模拟器
DEVICE_LIST=$(devecocli device list --json)
TARGET_DEVICE=$(echo $DEVICE_LIST | jq -r '.[0].id')
DEVICE_COUNT=$(echo $DEVICE_LIST | jq 'length')
if [ "${PRIOR_PHONE}" = true ] && [ $DEVICE_COUNT -gt 0 ] && [ "$TARGET_DEVICE" != "null" ]; then
    DEVICE_ARG="--device $TARGET_DEVICE"
else
    start_emulator
    DEVICE_LIST=$(devecocli device list --json)
    TARGET_DEVICE=$(echo $DEVICE_LIST | jq -r '.[0].id')
    DEVICE_ARG="--device $TARGET_DEVICE"
fi

# 1. 静态代码校验
devecocli lint --project $PROJECT_ROOT --json > lint_result.json
# 2. Debug增量编译
devecocli build --project $PROJECT_ROOT --mode debug --incremental --sign $SIGN_CONFIG
if [ $? -ne 0 ]; then echo "编译失败"; exit 1; fi
# 3. 一键安装启动App
devecocli run --project $PROJECT_ROOT $DEVICE_ARG --sign $SIGN_CONFIG
if [ $? -ne 0 ]; then echo "部署启动失败"; exit 1; fi
# 4. 导出结构化运行日志
devecocli log --filter $APP_BUNDLE --json --once > $LOG_OUT
# 可选关闭模拟器
[ "${EMU_AUTO_SHUTDOWN}" = true ] && stop_emulator
echo "流水线完成：lint_result.json(语法错误) $LOG_OUT(运行日志)"
```

### 4. hm_auto_release_package.sh 正式打包脚本

```bash
#!/bin/bash
source ./config.env
if [ $# -lt 1 ]; then echo "用法：$0 项目根目录"; exit 1; fi
PROJECT_ROOT=$1
mkdir -p ${DIST_DIR}
devecocli build --project $PROJECT_ROOT --mode release --sign $SIGN_CONFIG --output ${DIST_DIR}
[ $? -eq 0 ] && echo "Release包输出至 ${DIST_DIR}" || echo "打包失败"
```

### 赋予脚本执行权限

```bash
chmod +x *.sh
```

## 三、完整开发流程（两种模式：手动单命令 / AI 全自动流水线）

## 模式一：纯手动命令行开发（理解底层逻辑）

### 步骤 1：新建鸿蒙项目

```bash
devecocli create AiDemo \
--app-name com.example.aidemo \
--template empty-ability \
--api-level 26
# 进入项目目录，用VSCode手写ArkTS代码
cd AiDemo
code .
```

### 步骤 2：代码静态检查（提前发现语法 / 类型错误）

```bash
devecocli lint --project ./AiDemo --json > lint_error.json
```

### 步骤 3：设备 / 模拟器管理

```bash
# 查看所有在线真机/模拟器
devecocli device list --json
# 后台启动模拟器
devecocli emulator start --device-type phone --os-version "HarmonyOS 7.0.0(26)"
sleep 15
```

### 步骤 4：编译 + 安装 + 启动应用（替代 IDE 点击 Run）

```bash
devecocli run \
--project ./AiDemo \
--sign ./sign_config.json \
--auto-select-device
```

### 步骤 5：抓取运行日志，排查闪退、业务报错

```bash
devecocli log --filter com.example.aidemo --json --once > log.json
```

### 步骤 6：打包 Release 上架包

```bash
devecocli build --project ./AiDemo --mode release --sign ./sign_config.json --output ./dist
```

## 模式二：AI 全自动流水线（推荐，零人工 IDE 操作）

### 1. 创建新项目（执行初始化脚本）

```bash
./hm_auto_init.sh AiTodo empty-ability
```

### 2. AI 生成 / 修改代码后，一键全自动流水线

自动完成：设备检测→模拟器启停→Lint 校验→编译→安装启动→导出 JSON 日志

```bash
./hm_auto_build_run.sh ./AiTodo
```

### 3. AI 读取日志自动修复代码，循环迭代

Python 简易调用示例，集成本地 AI 工具：

```python
import subprocess, json
def pipeline(project):
    subprocess.run(["./hm_auto_build_run.sh", project])
    with open("lint_result.json","r",encoding="utf-8") as f:
        lint_err = json.load(f)
    with open("runtime_log.json","r",encoding="utf-8") as f:
        run_log = json.load(f)
    return lint_err, run_log

project_path = "./AiTodo"
max_loop = 8
count = 0
while count < max_loop:
    errors, logs = pipeline(project_path)
    # AI判断错误并自动修改代码
    if ai_detect_error(errors, logs):
        ai_fix_code(errors, logs, project_path)
        count += 1
        continue
    break
# 无错误后打包正式包
subprocess.run(["./hm_auto_release_package.sh", project_path])
```

### 4. 功能验收完成，导出 Release 安装包

```bash
./hm_auto_release_package.sh ./AiTodo
```

## 四、高频常用 CLI 命令汇总

1. **项目管理**`devecocli create` 新建工程；`devecocli docs search xxx` 查鸿蒙 API 文档
2. **代码检查**`devecocli lint --json` 结构化语法校验
3. **构建打包**`devecocli build --mode debug/release` 编译 HAP 包
4. **设备模拟器**`devecocli device list` 查看设备；`devecocli emulator start/stop` 模拟器启停
5. **部署运行**`devecocli run` 一键编译 + 安装 + 启动
6. **日志调试**`devecocli log --filter 包名 --json` 导出机器可读日志
7. **三方依赖**`devecocli ohpm install 依赖包` 安装鸿蒙第三方库
8. **AI 对接**`devecocli init --agent` 挂载 MCP 协议，对接本地 AI 编程工具

## 五、优势对比 DevEco IDE

1. 无任何鼠标点击操作，全部流程可脚本 / AI 调用；
2. 所有输出支持`--json`，AI 可自动解析报错、日志，实现自修复闭环；
3. 无需打开重型 IDE 图形界面，服务器、轻量化本地 AI 环境均可运行；
4. 模拟器、签名、编译全流程无人值守，仅人工最终体验 App 反馈问题。

## 六、常见踩坑解决

1. **SDK 路径报错**：重新执行`devecocli config set sdk.path`修改正确目录；
2. **模拟器启动失败**：提前执行`devecocli emulator image download`下载对应镜像；
3. **打包签名失败**：核对`sign_config.json`密码、ks 文件路径；
4. **Windows 脚本异常**：切换 Git Bash/WSL，路径使用 `/` 分隔符；
5. **JSON 日志为空**：安装`jq`，所有命令必须携带`--json`参数。