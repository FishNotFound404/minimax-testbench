# MiniMax 多模态能力测试报告

> 测试时间：2026-06-06
> 测试账号：Token Plan 订阅用户
> 测试环境：`https://api.minimaxi.com`（生产域名）

## 1. 能力覆盖总览

| # | 能力 | 状态 | 模块文件 | 测试脚本 |
| - | --- | --- | --- | --- |
| 1 | 语音合成 TTS | ✅ | `modules/tts.py` | `tests/test_tts.py` / `test_tts_variants.py` / `test_tts_polyphone.py` |
| 2 | 声音设计 | ✅ | `modules/voice_design.py` | `tests/test_voice_design.py` |
| 3 | 音色克隆 | ❌ 权限未开通 | `modules/voice_clone.py` | `tests/test_voice_clone.py` |
| 4 | 音乐生成 | ✅ | `modules/music.py` | `tests/test_music.py` / `test_music_advanced.py` / `test_music_cover.py` |
| 5 | 图片生成 | ✅ | `modules/image.py` | `tests/test_image.py` |
| 6 | 视频生成 | ✅ | `modules/video.py` | `tests/test_video.py` / `test_video_advanced.py` / `test_video_combined.py` |

**5/6 跑通**，唯一失败是音色克隆（套餐账号默认未开通，需 KYC 申请）。

## 2. 各能力详细结果

### 2.1 语音合成 TTS
- **端点**：`POST /v1/t2a_v2`
- **认证**：`Authorization: Bearer <token_plan_key>` 直接放 API Key
- **响应**：`data.audio` 字段为 hex 编码音频
- **测试覆盖**：
  - 基础 6 个文件：3 个系统音色（清澈男 / 少女 / 新闻女）+ 3 种情绪（happy / sad / angry）
  - 多音字测试：默认读音 vs 自定义拼音 `(chu3)(li3)` 注入

| 文件 | 音色 | 模型 | 大小 |
| --- | --- | --- | --- |
| `tts_male-qn-qingse_neutral.mp3` | 清澈男 | speech-2.6-hd | 59 KB |
| `tts_female-shaonv_neutral.mp3` | 少女 | speech-2.6-hd | 53 KB |
| `tts_anchor_neutral.mp3` | 新闻女 | speech-2.6-hd | 60 KB |
| `tts_qingse_happy.mp3` | 清澈男+happy | speech-2.6-hd | 60 KB |
| `tts_qingse_sad.mp3` | 清澈男+sad | speech-2.6-hd | 70 KB |
| `tts_qingse_angry.mp3` | 清澈男+angry | speech-2.6-hd | 61 KB |
| `tts_polyphone_default.mp3` | 默认多音字 | speech-2.6-hd | 78 KB |
| `tts_polyphone_custom.mp3` | 自定义拼音 | speech-2.6-hd | 95 KB |

### 2.2 声音设计
- **端点**：`POST /v1/voice_design`
- **必填**：`prompt`（音色描述）、`preview_text`（试听文本）
- **响应**：`voice_id`（自动生成或自定义）、`trial_audio`（试听 hex 编码）
- **测试产出**：
  - 自动生成 voice_id：`ttv-voice-2026060609351926-E7NGReqo`
  - 试听音频：`design_preview_*.mp3`（54 KB）
  - 合成验证：`designed_*.mp3`（54 KB）

### 2.3 音色克隆
- **端点**：`POST /v1/voice_clone`（需先调 `/v1/files/upload` 拿 `file_id`）
- **错误码 `2038: voice clone user forbidden`**
- **结论**：账号未开通复刻权限，需在控制台申请（参考 `/docs/faq/about-account` 页面）
- **参考音频**：`samples/ref_voice.wav`（当前用 TTS 输出充数，正式使用需替换为真人录音 10 秒~5 分钟）

### 2.4 音乐生成
- **端点**：`POST /v1/music_generation`
- **支持模型**：
  - `music-2.6`：标准版，仅 Token Plan / 付费用户
  - `music-2.6-free`：免费限速版
  - `music-cover`：翻唱，需要参考音频
- **测试产出**：

| 文件 | 模型 | 模式 | 大小 | 耗时 |
| --- | --- | --- | --- | --- |
| `indie_folk.mp3` | music-2.6 | 用户歌词 | 1.4 MB | ~30s |
| `summer_optimizer.mp3` | music-2.6 | 自动写词 | 3.9 MB | ~1min |
| `edm_instrumental.mp3` | music-2.6 | 纯音乐 | 5.7 MB | ~1min |
| `indie_to_edm_cover.mp3` | music-cover | 翻唱 | 1.4 MB | ~5min |

### 2.5 图片生成
- **端点**：`POST /v1/image_generation`
- **响应**：`data.image_urls`（默认 url，24h 有效）
- **测试产出**：
  - `__20260606_093707_0.png` 355 KB（16:9，image-01）
  - 注：首次跑时中文 prompt 被 slug 规则吃成空文件名，已改用 MD5 前 8 位做命名

### 2.6 视频生成
- **端点**：`POST /v1/video_generation`（异步） → `GET /v1/query/video_generation?task_id=...` → `GET /v1/files/retrieve?file_id=...`
- **支持模型**：
  - `MiniMax-Hailuo-2.3`（推荐，支持 6/10s、768P/1080P）
  - `MiniMax-Hailuo-02`
  - `T2V-01-Director`、`T2V-01`
- **运镜指令**：支持 15 种 `[指令]`（左/右移、推/拉、摇、变焦、跟随、固定等），可单条、组合、顺序使用
- **状态机**：`Preparing` → `Queueing` → `Processing` → `Success / Fail`
- **测试产出**：

| 文件 | 模型 | 分辨率 | 时长 | 大小 | 耗时 | 运镜 |
| --- | --- | --- | --- | --- | --- | --- |
| `cat_stretch.mp4` | Hailuo-2.3 | 768P | 6s | 1.0 MB | ~1.5min | 无 |
| `lake_1080p.mp4` | Hailuo-2.3 | 1080P | 6s | 4.2 MB | ~1.5min | `[Push in]` |
| `city_combo.mp4` | Hailuo-2.3 | 1080P | 6s | 4.9 MB | ~1.5min | `[Push in] + [Pan left]` |

## 3. 关键发现与踩坑点

### 3.1 认证与域名
- 官方域 `api.minimaxi.com`（不是 `MiniMax.chat` / `MiniMax.io`）
- Token Plan Key 直接当 Bearer Token 用即可
- 套餐 Key 与按量计费 API Key 不可互换

### 3.2 端点路径
| 能力 | 实际端点 |
| --- | --- |
| TTS | `/v1/t2a_v2`（不是 `/v1/text_to_speech`） |
| 声音设计 | `/v1/voice_design` |
| 音色克隆 | `/v1/voice_clone`（需先 `/v1/files/upload` 拿 file_id） |
| 音乐 | `/v1/music_generation` |
| 图片 | `/v1/image_generation` |
| 视频生成 | `/v1/video_generation` |
| 视频查询 | `/v1/query/video_generation?task_id=...` |
| 视频下载 | `/v1/files/retrieve?file_id=...` |
| 音色列表 | `/v1/get_voice` |
| 文件上传 | `/v1/files/upload`（multipart） |

### 3.3 下载兼容
- 图片/视频/试听音频的下载 URL 是 OSS 预签名 URL，**不能再带 `Authorization` 头**，否则 403
- 客户端 `download()` 方法已用裸 `requests.get` 处理

### 3.4 翻唱 prompt 限制
- `music-cover` 模型的 prompt **必须用英文**，中文 prompt 会让请求卡到超时
- 单次翻唱耗时 5~10 分钟，必须给 `timeout=900`（默认 300s 不够）

### 3.5 TTS 多音字
- `pronunciation_dict.tone` 支持三种格式：
  - 拼音+声调数字：`处理/(chu3)(li3)`
  - IPA：`read/(riːd)`
  - 纯文本替换：`resume/简历`
- 注入方式是行内 `(...)` 包裹，覆盖优先级高于默认读音

### 3.6 视频运镜指令
- 同一 `[]` 内的多个指令组合生效：`[左摇,推进]`
- 不同位置的 `[]` 按顺序生效：先 `[推进]` 再 `[拉远]`
- 自然语言描述也能控制运镜，但标准指令更精准

### 3.7 音色克隆权限
- 默认 Token Plan **不开通**复刻权限，错误码 2038
- 需在控制台 [账户相关 FAQ](https://platform.minimaxi.com/docs/faq/about-account) 申请 KYC

## 4. Token Plan 额度使用情况

| 能力 | 单次消耗 | 5h 窗口建议并发 |
| --- | --- | --- |
| TTS | 按字符计费（万字符 2 元） | 不限速 |
| 声音设计 | 试听 2 元/万字符 | 单并发足够 |
| 音乐生成 | 约 0.1~0.3 元/首 | 串行执行 |
| 图片生成 | 约 0.1 元/张 | 不限速 |
| 视频生成 | 6s/768P 约 1 元，1080P 约 2 元 | **强烈建议单并发**，否则 5h 窗口会打满 |

## 5. 项目代码结构

```
minimax_test/
├── config.py                  # 环境变量加载
├── minimax_client.py          # 统一客户端（POST/GET/upload/download）
├── modules/
│   ├── tts.py                 # 同步 TTS
│   ├── voice_design.py        # 自然语言设计新音色
│   ├── voice_clone.py         # 上传音频+克隆（需权限）
│   ├── music.py               # 音乐生成/翻唱
│   ├── image.py               # 图片生成
│   └── video.py               # 视频生成（异步轮询+下载）
├── tests/
│   ├── test_tts.py
│   ├── test_tts_variants.py
│   ├── test_tts_polyphone.py
│   ├── test_voice_design.py
│   ├── test_voice_clone.py
│   ├── test_music.py
│   ├── test_music_advanced.py
│   ├── test_music_cover.py
│   ├── test_image.py
│   ├── test_video.py
│   ├── test_video_advanced.py
│   └── test_video_combined.py
├── output/                    # 生成的 18 个文件
├── samples/
│   └── ref_voice.wav
├── .env / .env.example
├── requirements.txt
├── README.md
└── REPORT.md                  # 本文件
```

## 6. 下一步建议

1. **音色克隆**：去控制台申请 KYC 开通权限，把 `samples/ref_voice.wav` 换成自己的录音
2. **TTS 进阶**：`pronunciation_dict` 在有声书/教学场景可批量替换专业术语
3. **视频串联**：用 FastAPI 搭回调服务，接收 `callback_url` 推送，避免长轮询
4. **并发控制**：根据 5h 窗口余量调整视频任务的 `poll_interval` 与并发数
5. **历史接口**：MiniMax 平台保留 v1 / v2 旧接口，可对照 `/docs/faq/history-query` 看哪些能用
