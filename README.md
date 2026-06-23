# 小章鱼 Agent (Clawd Octo Agent)

一个可爱的紫色小章鱼主题，为 [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk) 设计。

![小章鱼](assets/octo-idle-follow.svg)

## 特点

- 🐙 30个 CSS 动画 SVG 状态
- 👀 跟踪鼠标的眼球（idle 状态）
- 🎵 戴耳机听歌摇晃（groove 状态）
- 😤 连续戳会烦躁（annoyed 反应）
- 🌙 完整睡眠序列（打哈欠→打盹→倒下→沉睡→醒来）
- 🔨 工作状态分层（打字→杂耍→建造，按并发会话数自动切换）
- 📦 迷你模式支持（扒屏幕边框风格）

## 安装

### 方法1：手动安装

1. 下载本仓库
2. 将整个文件夹复制到 Clawd on Desk 主题目录：
   ```
   %APPDATA%\clawd-on-desk\themes\octo-agent\
   ```
3. 重启 Clawd on Desk
4. 在设置中选择「小章鱼多线程 Agent」主题

### 方法2：通过 Clawd 设置

1. 打开 Clawd on Desk 设置
2. 主题 → 导入 → 选择本仓库的 `theme.json`

## 状态一览

### 自动检测状态

| 状态 | 触发条件 | 文件 |
|------|---------|------|
| idle | 无活动，鼠标静止 | octo-idle-follow.svg |
| thinking | Claude 思考中 | octo-working-thinking.svg |
| working | Claude 输出中 | octo-working-typing.svg |
| juggling | 多并发会话 | octo-working-juggling.svg |
| notification | 需要授权 | octo-notif-notification.svg |
| error | 出错 | octo-notif-error.svg |
| attention | 任务完成 | octo-notif-happy.svg |
| sweeping | 通知清理 | octo-notif-sweeping.svg |
| carrying | 传递中 | octo-notif-carrying.svg |
| groove | 音乐播放（需外部脚本） | octo-working-headphones-groove.svg |

### 睡眠序列

| 状态 | 阶段 |
|------|------|
| yawning | 打哈欠 |
| dozing | 打盹 |
| collapsing | 倒下 |
| sleeping | 沉睡 |
| waking | 醒来 |

### 工作分层（workingTiers）

| 并发会话数 | 显示 |
|-----------|------|
| 1 | 打字（typing） |
| 2 | 杂耍（juggling） |
| 3+ | 建造（building） |

### 多任务分层（jugglingTiers）

| 并发会话数 | 显示 |
|-----------|------|
| 1 | 杂耍（juggling） |
| 2+ | 戴耳机（headphones） |

### 交互反应

| 反应 | 触发方式 |
|------|---------|
| drag | 拖拽 |
| clickLeft | 左键点击 |
| clickRight | 右键点击 |
| double | 双击 |
| annoyed | 连续戳 |

### 迷你模式

扒在屏幕顶部边框上的小章鱼，支持 idle、alert、happy、enter、peek、crabwalk、enter-sleep、sleep、typing 共 9 个状态。

## 音乐检测（groove 状态）

Clawd on Desk 目前没有内置音乐检测功能。如果你希望「听歌时章鱼自动戴耳机」，可以：

1. 在主题的 `theme.json` 中已配置好 `groove` 状态
2. 使用外部脚本检测音乐播放，通过 Clawd 的本地 API 发送状态：
   ```
   POST http://127.0.0.1:23333/state
   {"state": "groove", "event": "MusicStart", "agent_id": "music-detector"}
   ```

详细方案见 [音乐检测脚本](https://github.com/rullerzhou-afk/clawd-on-desk/issues) 中的 feature request。

## 配色方案

| 元素 | 颜色 |
|------|------|
| 身体 | #C8A2D8 |
| 身体高光 | #D8BAE8 |
| 触手 | #9B6BB0 |
| 触手尖 | #B08ACC |
| 脸颊 | #F4A0B0 |
| 眼睛 | #2D2D2D |
| 嘴巴 | #E87090 |
| 平台 | #D4C7E0 |

## 开发

SVG 动画使用 CSS keyframes：
- `breathe` / `breatheSlow` — 呼吸起伏
- `float` — 漂浮
- `wobble` — 左右摇摆
- `shake` / `shakeHard` — 抖动
- `bounce` — 弹跳
- `sway` — 轻摇
- `blink` — 眨眼
- `look` — 眼睛高光移动
- `typepress` — 键盘按键
- `glow` — 发光
- `pulse` — 脉冲
- `ink` — 墨汁扩散
- `smoke` — 冒烟

## 许可

MIT License

## 致谢

- [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk) — 桌宠框架
- [Clawd Plana](https://github.com/rullerzhou-afk/clawd-plana) — 主题参考
