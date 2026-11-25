# 同时播放（SimulPlay）改动说明

本仓库是 [`Silent1566/webhtv`](https://github.com/Silent1566/webhtv) 的 fork，在保留上游全部功能的前提下，增加了「同时播放」：**画中画播放时切到 B 站等其他 App，本应用不再被音频焦点抢占而暂停，两路声音可同时输出**。

## 改了什么

| 文件 | 改动 |
| --- | --- |
| `setting/PlayerSetting.java` | 新增 `isPlayWithOthers()` / `putPlayWithOthers()`，默认 `true` |
| `player/PlayerManager.java` | 原生内核（MPV / IJK / 系统）：不申请音频焦点，并忽略 `onAudioFocusChange` |
| `player/exo/ExoUtil.java` | Media3 `setAudioAttributes(DEFAULT, !isPlayWithOthers())`，关闭内部焦点管理 |
| `ui/activity/PlaybackActivity.java` | 同时播放时，`onStop` 不再按「后台播放」策略暂停 |

耳机拔出（`ACTION_AUDIO_BECOMING_NOISY`）与用户主动暂停的行为保持不变。

## 为什么不是插件

上游自带的插件系统（`app/src/main/java/com/fongmi/android/tv/plugin/`）是 QuickJS 沙箱，SDK 1 只开放事件订阅、UI 槽位、HTTP、配置与日志，**没有播放器控制或音频焦点能力**，因此无法用「导入插件」的方式实现本功能，只能改宿主。

## 自动更新与自动构建

- `Sync Upstream`（每天 03:23 北京时间 + 手动）：调用 GitHub 官方 `merge-upstream` 接口把上游合入 `main`；冲突时自动开 issue。
- `Build SimulPlay APK`（push 到 `main` 或手动）：构建 debug APK 并发布到 `simulplay-latest` 预发布页，可直接下载安装（调试签名，需先卸载官方版）。

## 冲突时怎么办

上游若改动了上表四个文件的邻近代码，自动同步会失败并开 issue。处理方式：

```bash
git pull
git remote add upstream https://github.com/Silent1566/webhtv.git   # 仅首次
git fetch upstream
git merge upstream/main
# 按「不申请音频焦点」的意图解决冲突，确保三处判断仍然存在：
#   requestNativeAudioFocus / onNativeAudioFocusChanged 开头的 if (PlayerSetting.isPlayWithOthers()) return;
#   setAudioAttributes(..., !PlayerSetting.isPlayWithOthers())
git push
```

## 关闭同时播放

把 `PlayerSetting.isPlayWithOthers()` 的默认值改成 `false` 即可恢复系统默认行为；也可以在设置页接入开关（`putPlayWithOthers`）。
