# 同时播放（SimulPlay）+ 自建更新通道

本仓库是 [`Silent1566/webhtv`](https://github.com/Silent1566/webhtv) 的 fork，在保留上游全部功能的前提下增加了两件事：

1. **同时播放**：画中画播放时切到 B 站等其他 App，本应用不再被音频焦点抢占而暂停，两路声音可同时输出。
2. **自建更新通道**：App 内「关于 → 检查更新」的稳定版 / 测试版都改从本仓库读取，装一次之后可以直接在 App 内升级。

## 分支

| 分支 | 对应通道 | 说明 |
| --- | --- | --- |
| `main` | 稳定版 | 跟随上游 `main`，构建产物清单写入 `update-channel/mobile-arm64_v8a.json` |
| `beta` | 测试版 | 跟随上游 `beta`，构建产物清单写入 `update-channel/mobile-arm64_v8a-beta.json` |

两个分支都包含同时播放改动，上游同名文件在这两个分支上内容一致，因此补丁可以共用。

## 同时播放改了什么

| 文件 | 改动 |
| --- | --- |
| `setting/PlayerSetting.java` | 新增 `isPlayWithOthers()` / `putPlayWithOthers()`，默认 `true` |
| `player/PlayerManager.java` | 原生内核（MPV / IJK / 系统）：不申请音频焦点，并忽略 `onAudioFocusChange` |
| `player/exo/ExoUtil.java` | Media3 `setAudioAttributes(DEFAULT, !isPlayWithOthers())`，关闭内部焦点管理 |
| `ui/activity/PlaybackActivity.java` | 同时播放时，`onStop` 不再按「后台播放」策略暂停 |

耳机拔出（`ACTION_AUDIO_BECOMING_NOISY`）与用户主动暂停的行为保持不变。

### 为什么不是插件

上游自带的插件系统（`app/src/main/java/com/fongmi/android/tv/plugin/`）是 QuickJS 沙箱，SDK 1 只开放事件订阅、UI 槽位、HTTP、配置与日志，**没有播放器控制或音频焦点能力**，因此无法用「导入插件」的方式实现本功能，只能改宿主。

## 更新通道改了什么

`utils/Github.java` 里所有更新地址都指向本仓库：

| 常量 / 方法 | 现在指向 |
| --- | --- |
| `getChannelAsset(name)` | `https://github.com/qwqqvq123456/webhtv/releases/download/update-channel/<name>` |
| `getGithubLatestAsset(name)` | `https://github.com/qwqqvq123456/webhtv/releases/latest/download/<name>` |
| `getGithubReleaseAsset(tag, name)` | `https://github.com/qwqqvq123456/webhtv/releases/download/<tag>/<name>` |
| `getReleasesApi()` / `getLatestReleaseApi()` | `https://api.github.com/repos/qwqqvq123456/webhtv/releases...` |
| `getCnbMirrorAsset(name)` | 返回空串，**主动停用上游 CNB 镜像** |
| `GithubProxy.probeUrl(source)` | 代理测速改用 `Github.REPO_OWNER/REPO_NAME`，探测目标 `update-channel/update.json` |

CNB 镜像必须停用：检查更新时的顺序是「本仓库清单 → CNB 镜像 → Releases API」，若保留镜像，一次网络抖动就会读到上游清单，App 会提示下载官方包，装上去就把本 fork 覆盖掉了。

换仓库只需改 `Github.REPO_OWNER` / `Github.REPO_NAME` 两个常量，其余地址都是拼出来的。

## 清单格式

`update-channel` 是一个固定 tag 的预发布 release，只放清单不放 APK：

```json
{
  "name": "v5.6.0-beta-202611260200",
  "versionName": "5.6.0",
  "channel": "beta",
  "code": 560,
  "apk": "https://github.com/qwqqvq123456/webhtv/releases/download/v5.6.0-beta-202611260200/mobile-arm64_v8a-beta.apk",
  "size": 201000000,
  "sha256": "…",
  "notes": "- 构建提交摘要"
}
```

判定规则（`bean/Update.java` + `utils/AppVersion.java`）：`code` 大于已装版本才算更新；`code` 相等时比较 tag 里 12/14 位时间戳（`yyyyMMddHHmm`，北京时间）。因此 tag 的时间戳必须是**构建发布时刻**，早于已装版本就永远不会提示更新。

`update-channel` 里另有一个 `update.json`，只作为 `GithubProxy.probeUrl()` 的连通性探测目标，不含版本信息。

## 签名

构建使用仓库 Secrets 里的固定 keystore（`KEYSTORE_BASE64` / `KEYSTORE_PASSWORD` / `KEY_ALIAS` / `KEY_PASSWORD`），保证每次产出的 APK 签名一致 —— `Updater.signaturesMatch` 会比对已装应用与新包的签名指纹，不一致会直接拒绝安装。

> 官方版用的是上游作者的私钥，无法复用。因此**第一次必须卸载官方版**，装一次本仓库的包，之后才能走 App 内更新。

## 自动同步与自动构建

- `Sync Upstream`（每天北京时间 03:23 + 手动）：对 `main` 和 `beta` 分别调用 GitHub 官方 `merge-upstream`；冲突时按分支开 issue。成功后自动触发对应通道的构建。
- `Build SimulPlay APK`（push 到任一分支或手动）：release 变体 + 固定签名，发布 `v<versionName>[-beta]-<时间戳>` release，并把清单覆盖写入 `update-channel`。

手动构建可选 `channel`（stable/beta）、`flavor`（mobile/leanback × arm64/armv7）和 `optimize`（开启 R8，体积更小但更慢）。

## 冲突时怎么办

上游若改动了上表四个文件或 `Github.java` 的邻近代码，自动同步会失败并开 issue：

```bash
git pull
git remote add upstream https://github.com/Silent1566/webhtv.git   # 仅首次
git fetch upstream
git merge upstream/main        # 或 upstream/beta
# 按「不申请音频焦点」的意图解决冲突，确保三处判断仍然存在：
#   requestNativeAudioFocus / onNativeAudioFocusChanged 开头的 if (PlayerSetting.isPlayWithOthers()) return;
#   setAudioAttributes(..., !PlayerSetting.isPlayWithOthers())
git push
```

## 关闭同时播放

把 `PlayerSetting.isPlayWithOthers()` 的默认值改成 `false` 即可恢复系统默认行为；也可以在设置页接入开关（`putPlayWithOthers`）。
