# 資料前處理與 GPT-4o Fine-tuning

本文件詳細描述了該專案從資料收集、資料清洗、標籤生成、資料拆分到模型微調的完整流程，也引用 OpenAI 官方文件中的相關 API 資料，幫助你了解專案流程。

## 專案概述

專案包含從穿搭平台 [wear.jp](https://wear.jp/) 爬取該平台每月網路評選前一百名最佳穿搭資料。接著，進行資料清洗，並使用 OpenAI 的 Vision 和 Text Generation API 進行標籤生成，最終 fine-tune GPT-4o 模型。

## 專案結構

- `scrape.py`：負責從 wear.jp 爬取資料的腳本。
- `cleanse.py`：負責清洗和預處理爬取資料的腳本。
- `vision.py`：使用 OpenAI 的 Vision API 生成圖片標籤的腳本。
- `profile.py`：使用 OpenAI 的 Text Generation API 生成用戶自介標籤的腳本。
- `form_dataset.py`：將資料拆分成適合微調 GPT-4o 模型的訓練集的腳本。

## 流程概述

### 1. 資料收集 (`scrape.py`)

`scrape.py` 腳本負責從 wear.jp 爬取用戶的穿搭照片和自我介紹資料。
使用 Python 的 `requests` 和 `BeautifulSoup` 進行網路爬蟲。

### 2. 資料清洗 (`cleanse.py`)

`cleanse.py` 腳本負責處理爬取到的資料。具體步驟包括：
- 轉換 URL 以確保其完整性。
- 解析整數並保留必要的欄位，如性別、身高和自我介紹。

### 3. 圖片標籤生成 (`vision.py`)

`vision.py` 腳本使用 OpenAI 的 [Vision API](https://platform.openai.com/docs/guides/vision) 為穿搭照片生成詳細標籤。具體步驟包括：
- 發送圖片 URL 到 Vision API。
- 接收並處理 API 回應，生成描述圖片中穿搭的詳細標籤。
- 驗證標籤格式的正確性。

#### 使用的 Prompt

```
仔細觀察這張圖片中的人物，精確且細膩地描述他的外貌和穿著的所有服飾及配件，提供一個詳細的 multi-tags 列表。
確保涵蓋每一個細節，包括顏色、材質、設計、功能和搭配。
每類 tag 可有多個以涵蓋所有細節。回覆時按以下格式分別描述模特、上半身、下半身和鞋子，不可包含多餘內容。
    
json
{
    "模特": "膚色:顏色, 種族:類型, 髮型:描述, 髮色:描述, 身材:描述, 面部特徵:描述, 其他特徵:描述",
    "上半身": "顏色:顏色, 服裝類型:類型, 設計特點:描述, 材質:材質, 配件:描述（無可略）, 細節:描述",
    "下半身": "顏色:顏色, 服裝類型:類型, 設計特點:描述, 材質:材質, 配件:描述（無可略）, 細節:描述",
    "鞋子": "顏色:顏色, 服裝類型:類型, 設計特點:描述, 材質:材質, 細節:描述"
}
```

### 4. 自介標籤生成 (`profile.py`)

`profile.py` 腳本使用 OpenAI 的 [Text Generation API](https://platform.openai.com/docs/guides/text-generation/chat-completions-api) 將用戶自介轉換為與穿搭相關的標籤。

#### 使用的 Prompt

```
仔細閱讀用戶的自我介紹，並將其轉換成與穿搭可能相關的標籤列表。
忽略不重要的資訊，如社交媒體平台名稱、品牌名稱、活動名稱、日期等。
確保涵蓋所有可能與穿搭習慣及偏好的細節。
回覆時請用繁體中文，並以逗點間隔標籤（tag1,tag2,tag3,...），不可包含多餘內容。
```

具體步驟包括：
- 發送用戶自介到 Text Generation API。
- 忽略社交媒體帳號、品牌名稱、活動名稱和日期等不重要資訊。
- 接收並處理 API 回應，生成與穿搭相關的標籤。

### 5. 資料拆分 (`form_dataset.py`)

`form_dataset.py` 腳本將每筆清洗後的資料拆分成六筆訓練資料。具體步驟包括：
- 已知上半身，推薦下半身。
- 已知上半身，推薦鞋子。
- 已知下半身，推薦上半身。
- 已知下半身，推薦鞋子。
- 已知鞋子，推薦上半身。
- 已知鞋子，推薦下半身。

最終，範例訓練資料集如下：

```
{"prompt": f"{common_info}, 上衣: {upper}", "completion": f"下身: {lower}"},
{"prompt": f"{common_info}, 上衣: {upper}", "completion": f"鞋子: {shoes}"},
{"prompt": f"{common_info}, 下身: {lower}", "completion": f"上衣: {upper}"},
{"prompt": f"{common_info}, 下身: {lower}", "completion": f"鞋子: {shoes}"},
{"prompt": f"{common_info}, 鞋子: {shoes}", "completion": f"上衣: {upper}"},
{"prompt": f"{common_info}, 鞋子: {shoes}", "completion": f"下身: {lower}"}
...
```

### 6. 模型微調

使用 OpenAI 的 [Fine-tuning API](https://platform.openai.com/docs/guides/fine-tuning) 進行模型微調。具體步驟包括：
- 使用 OpenAI 的 CLI 工具準備數據。
- 提交準備好的數據進行微調。
- 監控微調進度。
- 使用微調後的模型生成基於用戶偏好的穿搭推薦。

