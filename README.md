# Home Assistant 威盛智能喂鱼器自定义集成 (VSON Fish Feeder)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

适用于威盛 (VSON / 惠视达) 系列 WiFi 智能喂鱼器（型号包含 WP8615、WP8621、WP8621N 等）的 Home Assistant 自定义集成。支持通过云端通道实现实时状态同步、左/右料仓手动投喂、水泵控制（WP8621 系列）、换水提醒与计时重置。

---

## 🌟 支持功能

- **实体与传感器**：
  - 🔋 **电池电量** (`sensor.battery`)：电池剩余百分比及电量格数
  - ⚡ **充电状态** (`binary_sensor.is_charging`)：是否处于充电中
  - 🔌 **外部电源** (`binary_sensor.power_plugged`)：是否接入外接供电
  - 📶 **在线状态** (`binary_sensor.connectivity`)：设备是否在线连接
  - ⚠️ **缺粮告警** (`binary_sensor.food_shortage`)：检测储粮仓是否缺粮
  - 🕒 **上次投喂时间** (`sensor.last_feed_left` / `sensor.last_feed_right`)：记录左仓和右仓最近一次投喂时间
  - 💧 **换水洁净度** (`sensor.water_cleanliness`)：根据换水周期与天数计算的清洁度百分比
  - 📅 **上次换水时间 & 周期** (`sensor.last_water_change` / `sensor.water_change_period`)
  - 🚨 **换水到期提醒** (`binary_sensor.water_change_due`)

- **控制按键与开关**：
  - 🐟 **左仓立即投喂** (`button.feed_left`)
  - 🐟 **右仓立即投喂** (`button.feed_right`)
  - 🌊 **水泵控制开关** (`switch.pump_power`)：支持 WP8621 / WP8621N 等带水泵型号
  - 🔄 **重置换水计时** (`button.reset_water_change`)
  - 🛠️ **服务支持**：`vson_feeder.feed` 及 `vson_feeder.reset_water_change`

---

## 📦 安装与配置说明

### 第一步：设备配网与获取 MAC 地址
1. 手机先下载官方的 **「美意智能」** APP。
2. 打开 APP 按照向导提示，把喂鱼器设备连接上无线网络（Wi-Fi）。
3. 设备连接成功后，在 APP 的设备详情界面或路由器后台设备列表中，**记下设备的 MAC 地址**（格式如 `86:15:02:FB:BB:A3` 或 `86:21:02:63:B8:EF`）。

### 第二步：安装集成到 Home Assistant

#### 方式一：通过 HACS / Marketplace 安装（推荐）
1. 打开 Home Assistant -> **Marketplace** (或 HACS)。
2. 点击右上角菜单 -> **自定义存储库** (Custom repositories)。
3. 输入存储库地址：`https://github.com/chenpinetree/ha-vson-feeder`，类别选择 **集成** (Integration)。
4. 点击添加后，在列表中搜索 **威盛智能喂鱼器** 并点击 **下载**。
5. 重启 Home Assistant Core。

#### 方式二：手动安装
将本项目中的 `custom_components/vson_feeder` 文件夹复制到 Home Assistant 配置目录的 `custom_components` 目录下，并重启 Home Assistant。

---

## ⚙️ 添加设备到 Home Assistant

1. 重启完成后，进入 Home Assistant **设置** -> **设备与服务** -> **添加集成**。
2. 搜索 `威盛智能喂鱼器` 或 `vson_feeder`。
3. 输入第一步中记下的设备 **MAC 地址**。
4. 点击提交即可自动完成绑定，设备卡片及全部实体将自动生成。
