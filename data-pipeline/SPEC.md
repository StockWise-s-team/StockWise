# StockWise Data-Pipeline — Specification

> Tài liệu này ghi nhận **trạng thái thực tế** của codebase, không phải spec lý thuyết. Mỗi mục đánh dấu `✅` (hoàn thiện), `⚠️` (còn thiếu/thức cần bổ sung), hoặc `❌` (chưa có).

---

## I. YÊU CẦU CHỨC NĂNG (Functional Requirements)

### 1. Nguồn dữ liệu & Thu thập

#### 1.1 Thu thập giá cổ phiếu (Stream A)
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 1.1.1 | Gọi VnStock API (KBS source), lấy OHLCV 30 ngày cho mỗi mã | ✅ Hoàn thiện | `app/stream_a/fetchers/vnstock_fetcher.py` |
| 1.1.2 | Hỗ trợ rate-limit: retry 3 lần, backoff 60s | ✅ Hoàn thiện | `vnstock_fetcher.py` |
| 1.1.3 | Chạy async trong event loop riêng (tránh blocking scheduler thread) | ✅ Hoàn thiện | `scheduler.py` `_run_async()` |
| 1.1.4 | Delay 4 giây giữa các mã để tránh quá tải API | ✅ Hoàn thiện | `scheduler.py` line 157 |

#### 1.2 Thu thập chỉ số tài chính (Stream A)
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 1.2.1 | Gọi Yahoo Finance API (TTM ratios: P/E, P/B, EPS, ROE, ROA) | ✅ Hoàn thiện | `app/stream_a/fetchers/yahoo_finance_fetcher.py` |
| 1.2.2 | Fallback graceful khi không lấy được dữ liệu | ✅ Hoàn thiện | `yahoo_finance_fetcher.py` — `safe_float` trả None |
| 1.2.3 | Auto-seed company_info + financial_ratios cho mã mới thêm | ✅ Hoàn thiện | `scheduler.py` `_auto_seed_missing_metadata()` |
| 1.2.4 | Seed script dùng VnStock/VCI, Stream A dùng Yahoo Finance — nhất quán nguồn annual vs TTM | ⚠️ Đã ghi nhận | Seed lấy annual, Stream A lấy TTM |

#### 1.3 Thu thập tin tức từ CafeF (Stream B)
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 1.3.1 | Crawl sitemap — parse sitemap XML, lấy URLs + lastmod | ✅ Hoàn thiện | `app/stream_b/crawlers/cafef_crawler.py` |
| 1.3.2 | Tối đa 50 bài/lần | ✅ Hoàn thiện (MAX_ARTICLES=50) | `cafef_crawler.py` line 21 |
| 1.3.3 | Giới hạn 30 ngày gần nhất | ✅ Hoàn thiện (CUTOFF_DAYS=30) | `cafef_crawler.py` line 22 |
| 1.3.4 | Trích xuất tiêu đề, nội dung, thời gian, symbol tags từ article HTML | ✅ Hoàn thiện | `_parse_article()` |
| 1.3.5 | Retry logic: 3 attempts, exponential backoff | ✅ Hoàn thiện | `@retry` decorator |
| 1.3.6 | Delay 1s giữa các article request | ✅ Hoàn thiện | line 60 |

#### 1.4 Thu thập tin tức từ Vietstock (Stream B)
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 1.4.1 | Crawl sitemap — primary: regex extraction (vì sitemap rất lớn ~32MB) | ✅ Hoàn thiện | `app/stream_b/crawlers/vietstock_crawler.py` lines 141-144 |
| 1.4.2 | Tối đa 50 bài/lần | ✅ Hoàn thiện (MAX_ARTICLES=50) | `vietstock_crawler.py` line 21 |
| 1.4.3 | Giới hạn 30 ngày gần nhất | ✅ Hoàn thiện | `_is_within_cutoff()` — so sánh year-month |
| 1.4.4 | Parse thời gian tương đối ("3 giờ trước" → datetime) | ✅ Hoàn thiện | `_parse_relative_date()` regex + timedelta |
| 1.4.5 | Sort URLs theo year/month descending trước khi crawl | ✅ Hoàn thiện | lines 74-84 |
| 1.4.6 | Retry + delay 1s | ✅ Hoàn thiện | `@retry` + `asyncio.sleep` |

#### 1.5 Bật/tắt nguồn tin
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 1.6.1 | API bật/tắt nguồn: `PATCH /news-sources/{source_id}` | ✅ Hoàn thiện | `app/api/routes.py` lines 66-94 |
| 1.6.2 | Invalidate cache khi toggle (5-min cache trong SourceRepository) | ✅ Hoàn thiện | `routes.py` line 79 `SourceRepository().invalidate()` |
| 1.6.3 | Stream B chỉ crawl nguồn active | ✅ Hoàn thiện | `scheduler.py` line 252 |

---

### 2. Làm sạch & Xử lý dữ liệu

#### 2.1 Validate dữ liệu giá
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 2.1.1 | Giá trong khoảng 0.001–1,000,000 VND | ✅ Hoàn thiện | `app/stream_a/transformers/price_transformer.py` lines 81-85 |
| 2.1.2 | High ≥ Low | ✅ Hoàn thiện | `_validate_ohlc()` lines 52-56 |
| 2.1.3 | High ≥ Open và High ≥ Close | ✅ Hoàn thiện | lines 57-64 |
| 2.1.4 | Low ≤ Open và Low ≤ Close | ✅ Hoàn thiện | lines 65-72 |
| 2.1.5 | Volume ≥ 0 | ✅ Hoàn thiện | `_parse_volume()` lines 40-49 |

#### 2.2 Validate chỉ số tài chính
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 2.2.1 | P/E, P/B, EPS phải ≥ 0 | ✅ Hoàn thiện | `app/stream_a/transformers/ratio_transformer.py` lines 108-111 |
| 2.2.2 | ROE, ROA có thể âm (lỗi doanh nghiệp) | ✅ Hoàn thiện | `RATIO_CAN_BE_ANY = {"roe", "roa"}` line 21 |
| 2.2.3 | Giới hạn max: P/E ≤ 1000, P/B ≤ 1000, EPS ≤ 100,000, ROE/ROA ≤ 1.0 | ✅ Hoàn thiện | MAX_* constants + `_validate_ratio()` |
| 2.2.4 | Giá trị None được phép (doanh nghiệp không có chỉ số) | ✅ Hoàn thiện | lines 56-57 `_validate_ratio` |

#### 2.3 Strip HTML
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 2.3.1 | Loại bỏ thẻ HTML | ✅ Hoàn thiện | `app/stream_b/transformers/news_transformer.py` `_strip_html()` |
| 2.3.2 | Loại bỏ script, style, nav, header, footer | ✅ Hoàn thiện | `soup.find_all(["script", "style", "nav", "header", "footer"])` line 81 |
| 2.3.3 | Collapse nhiều khoảng trắng về 1 | ✅ Hoàn thiện | `re.sub(r"\s{2,}", " ", text)` line 84 |

#### 2.4 Trích xuất mã cổ phiếu
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 2.4.1 | Regex tìm mã [A-Z]{3,4} | ✅ Hoàn thiện | `STOCK_SYMBOL_RE` regex line 18-19 |
| 2.4.2 | Loại trừ từ thông thường (THE, AND, HNX, HSX...) | ✅ Hoàn thiện | `_extract_symbols()` lines 95-99 |
| 2.4.3 | ⚠️ Danh sách stopwords chưa đầy đủ — thiếu nhiều từ phổ biến (VN30, VN100, HNX, UPCAM...) nằm trong list nhưng trùng lặp vì có cả uppercase và lowercase | Cần cải thiện | `news_transformer.py` line 97-98 |
| 2.4.4 | CafeF/Vietstock: lấy symbol tags trực tiếp từ page HTML | ✅ Hoàn thiện | `cafef_crawler.py` lines 183-189 |

#### 2.5 Chunking văn bản
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 2.5.1 | Cắt bài dài thành đoạn ~500 ký tự | ✅ Hoàn thiện | `app/stream_b/embedder.py` `RecursiveCharacterTextSplitter(chunk_size=500)` |
| 2.5.2 | Overlap 50 ký tự giữa các đoạn | ✅ Hoàn thiện | `chunk_overlap=50` |
| 2.5.3 | Dùng LangChain RecursiveCharacterTextSplitter | ✅ Hoàn thiện | `langchain_text_splitters` |

#### 2.6 Vector hóa văn bản
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 2.6.1 | Vector hóa bằng OpenAI (1536 chiều) | ✅ Hoàn thiện | `app/stream_b/embedder.py` `_embed_openai()` |
| 2.6.2 | Fallback sentence-transformers local (384 chiều) | ✅ Hoàn thiện | `_embed_local()` |
| 2.6.3 | Tự động tạo Qdrant collection nếu chưa có | ✅ Hoàn thiện | `ensure_collection()` |
| 2.6.4 | Cosine similarity search | ✅ Hoàn thiện | `Distance.COSINE` |

---

### 3. Lưu trữ

#### 3.1 Lưu giá cổ phiếu
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 3.1.1 | Upsert vào bảng `stock_prices` theo (symbol, trade_date) | ✅ Hoàn thiện | `app/stream_a/repositories/price_repository.py` `upsert_prices()` |
| 3.1.2 | Đã có thì ghi đè | ✅ Hoàn thiện | `ON CONFLICT (symbol, trade_date) DO UPDATE` |

#### 3.2 Lưu chỉ số tài chính
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 3.2.1 | Upsert vào bảng `financial_ratios` theo (symbol, period) | ✅ Hoàn thiện | `app/stream_a/repositories/price_repository.py` `upsert_ratios()` |
| 3.2.2 | ⚠️ **Seed script không upsert EPS** — `seed.py` line 289-296 upsert thiếu `eps` field | Cần fix | `app/scripts/seed.py` |

#### 3.3 Lưu bài báo
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 3.3.1 | Insert vào `news_articles`, trùng URL thì bỏ qua | ✅ Hoàn thiện | `app/stream_b/repositories/news_repository.py` `insert_articles_bulk()` |
| 3.3.2 | Bulk insert (performance) | ✅ Hoàn thiện | `psycopg2.extras.execute_values` |

#### 3.4 Lưu vector tin tức
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 3.4.1 | Upsert vectors + payload vào Qdrant collection `news_chunks` | ✅ Hoàn thiện | `app/stream_b/embedder.py` `embed_and_upsert()` |
| 3.4.2 | Tìm kiếm theo cosine similarity | ✅ Hoàn thiện | Qdrant `Distance.COSINE` |

#### 3.5 Quản lý mã theo dõi
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 3.5.1 | Thêm mã: `POST /tracked-symbols` — tự động seed + synthesis | ✅ Hoàn thiện | `app/api/routes.py` lines 112-182 |
| 3.5.2 | Xóa mã: `DELETE /tracked-symbols/{symbol}` | ✅ Hoàn thiện | lines 185-196 |
| 3.5.3 | Liệt kê: `GET /tracked-symbols` | ✅ Hoàn thiện | lines 99-109 |

#### 3.6 Lưu lịch sử wiki
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 3.6.1 | Mỗi lần cập nhật wiki đều lưu bản cũ vào `company_wiki_history` | ✅ Hoàn thiện | `app/synthesis/wiki_repository.py` `insert_history()` |
| 3.6.2 | Không xóa bản cũ | ✅ Hoàn thiện | chỉ INSERT, không DELETE |

---

### 4. Tổng hợp AI

#### 4.1 Tổng hợp wiki công ty
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 4.1.1 | Gọi LLM ghép wiki cũ + 20 bài báo mới nhất + 5 ngày giá + chỉ số tài chính | ✅ Hoàn thiện | `app/synthesis/synthesis_agent.py` + `merger.py` |
| 4.1.2 | Retry logic: 3 attempts, exponential backoff | ✅ Hoàn thiện | `merger.py` `@retry` decorator |
| 4.1.3 | Parse JSON response từ LLM | ✅ Hoàn thiện | `_parse_response()` |
| 4.1.4 | Validate required fields trong response | ✅ Hoàn thiện | `_WIKI_REQUIRED_FIELDS` check |

#### 4.2 Duy trì phiên bản wiki
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 4.2.1 | Tự động tăng version mỗi lần cập nhật | ✅ Hoàn thiện | `wiki_repository.py` `upsert_wiki()` — `version = company_wiki.version + 1` |
| 4.2.2 | Lưu đủ lịch sử vào `company_wiki_history` | ✅ Hoàn thiện | `insert_history()` được gọi sau upsert |

#### 4.3 Override dữ liệu authoritative
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 4.3.1 | Sau khi LLM tổng hợp, `company_name/sector/business_summary` luôn lấy từ DB chuẩn | ✅ Hoàn thiện | `merger.py` lines 89-97 |
| 4.3.2 | `financials_snapshot` luôn override bằng tỷ số thực từ DB | ✅ Hoàn thiện | lines 100-105 |

---

### 5. Giao tiếp nội bộ (RabbitMQ)

#### 5.1 Gửi thông báo giá cổ phiếu
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 5.1.1 | Publish `price.updated` lên RabbitMQ `market.exchange` | ✅ Hoàn thiện | `app/rabbitmq/producer.py` + `scheduler.py` lines 213-224 |
| 5.1.2 | Message persistent (durable) | ✅ Hoàn thiện | `DeliveryMode.PERSISTENT` |
| 5.1.3 | Topic exchange | ✅ Hoàn thiện | `aio_pika.ExchangeType.TOPIC` |

#### 5.2 Gửi thông báo tin tức mới
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 5.2.1 | Publish `raw.ingested` lên RabbitMQ `news.exchange` | ✅ Hoàn thiện | `scheduler.py` lines 327-339 |
| 5.2.2 | Orchestrator consume message → trigger synthesis | ✅ Hoàn thiện | `app/synthesis/orchestrator.py` `_on_message()` |

---

### 6. Scheduling & Chạy Pipeline

#### 6.1 Chạy định kỳ Stream A
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 6.1.1 | Mỗi 4 giờ tự động fetch giá + chỉ số tài chính | ✅ Hoàn thiện | `app/scheduler.py` job `stream_a` |
| 6.1.2 | Chạy lần đầu ngay khi startup | ✅ Hoàn thiện | `next_run_time=datetime.now()` |
| 6.1.3 | Auto-seed metadata cho symbols mới | ✅ Hoàn thiện | `_auto_seed_missing_metadata()` |

#### 6.2 Chạy định kỳ Stream B
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 6.2.1 | Mỗi 4 giờ tự động crawl tin tức từ 3 nguồn | ✅ Hoàn thiện | `scheduler.py` job `stream_b` |
| 6.2.2 | Crawl song song (asyncio.gather) | ✅ Hoàn thiện | lines 255-258 |
| 6.2.3 | Graceful error handling — 1 nguồn fail không ảnh hưởng 2 nguồn còn lại | ✅ Hoàn thiện | `return_exceptions=True` |

#### 6.3 Chạy định kỳ Stream C (Synthesis)
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 6.3.1 | Mỗi 4 giờ tự động tổng hợp wiki cho tất cả mã | ✅ Hoàn thiện | `scheduler.py` job `synthesis` |
| 6.3.2 | Per-symbol error isolation — 1 mã fail không dừng toàn bộ | ⚠️ **Có bug** — `synthesis_agent.py` line 66 re-raises exception | `app/synthesis/synthesis_agent.py` |
| 6.3.3 | Chạy 1 symbol tại một thời điểm (không parallel) | ✅ Hoàn thiện | `scheduler.py` line 383 |

#### 6.4 Xem trạng thái scheduler
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 6.4.1 | API trả về scheduler đang chạy không | ✅ Hoàn thiện | `app/api/routes.py` `pipeline_status()` |
| 6.4.2 | Lần chạy tiếp theo của mỗi stream | ✅ Hoàn thiện | `next_dt()` helper |
| 6.4.3 | ⚠️ **Không trả về last_run / symbols_processed thực tế** — response hard-code `status: "idle"`, `last_run: null` | Cần cải thiện | `routes.py` lines 520-528 |

---

### 7. API Quản trị (FastAPI)

#### 7.1 Quản lý nguồn tin
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.1.1 | `GET /news-sources` — danh sách nguồn | ✅ Hoàn thiện | `routes.py` lines 59-63 |
| 7.1.2 | `PATCH /news-sources/{source_id}` — bật/tắt | ✅ Hoàn thiện | lines 66-94 |

#### 7.2 Quản lý mã theo dõi
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.2.1 | `GET /tracked-symbols` | ✅ Hoàn thiện | lines 99-109 |
| 7.2.2 | `PUT` (POST) thêm mã — tự động seed + synthesis | ✅ Hoàn thiện | lines 112-182 |
| 7.2.3 | `DELETE /tracked-symbols/{symbol}` | ✅ Hoàn thiện | lines 185-196 |

#### 7.3 Seed dữ liệu giá
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.3.1 | `POST /scripts/seed` — trigger seed giá | ✅ Hoàn thiện | `routes.py` lines 249-272 |
| 7.3.2 | Batch 18 mã, rate limit 65s | ⚠️ **Có trong logic nhưng không expose qua response** — `SeedResponse` có fields `symbols_seeded`, `price_rows`, `wiki_rows` nhưng luôn trả 0/"[]" | `routes.py` `_seed_sync()` |
| 7.3.3 | Hỗ trợ retry khi bị giới hạn | ✅ Hoàn thiện | `_seed_sync()` lines 321-345 |
| 7.3.4 | Dry-run mode | ✅ Hoàn thiện | `SeedRequest.dry_run` |

#### 7.4 Seed wiki công ty
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.4.1 | Trigger seed wiki cho nhiều mã | ✅ Hoàn thiện | `POST /scripts/seed` + `wiki_only` flag |

#### 7.5 Xem danh sách wiki
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.5.1 | `GET /company-wiki` — paginated list | ✅ Hoàn thiện | `routes.py` lines 201-235 |
| 7.5.2 | `GET /company-wiki/{symbol}` — wiki 1 công ty | ✅ Hoàn thiện | lines 238-244 |

#### 7.6 Trigger synthesis thủ công
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.6.1 | `POST /synthesis/trigger` — kích hoạt Stream C ngay cho danh sách mã | ✅ Hoàn thiện | `routes.py` lines 437-500 |

#### 7.7 Xem tiến độ pipeline
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.7.1 | `GET /pipeline/progress` — SSE streaming | ✅ Hoàn thiện | `routes.py` lines 533-581 |
| 7.7.2 | `GET /pipeline/progress/poll` — polling fallback | ✅ Hoàn thiện | lines 584-597 |

#### 7.8 Xem trạng thái pipeline
| # | Chức năng | Trạng thái | File(s) |
|---|-----------|-----------|---------|
| 7.8.1 | `GET /pipeline/status` — scheduler status + next run times | ✅ Hoàn thiện | lines 505-528 |
| 7.8.2 | `GET /pipeline/runs` — lịch sử pipeline với pagination | ✅ Hoàn thiện | lines 602-611 |
| 7.8.3 | `GET /pipeline/runs/stats` — thống kê 7 ngày | ✅ Hoàn thiện | lines 614-618 |
| 7.8.4 | `GET /pipeline/runs/recent` — N lần chạy gần nhất | ✅ Hoàn thiện | lines 621-625 |
| 7.8.5 | `GET /pipeline/runs/{run_id}` — chi tiết 1 run + per-symbol results | ✅ Hoàn thiện | lines 628-635 |

---

## II. YÊU CẦU PHI CHỨC NĂNG (Non-Functional Requirements)

### NFR-1. Hiệu năng (Performance)

| # | Yêu cầu | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| NFR-1.1 | Batch 18 mã, rate limit 65s giữa các batch (VnStock) | ✅ | `seed.py` line 312-317, `routes.py` `_seed_sync()` |
| NFR-1.2 | 4s delay giữa mã trong Stream A | ✅ | `scheduler.py` line 157 |
| NFR-1.3 | 1–1.5s delay giữa article requests trong Stream B | ✅ | `cafef_crawler.py` line 60, `vietstock_crawler.py` line 106 |
| NFR-1.4 | Crawl song song 3 nguồn tin (asyncio.gather) | ✅ | `scheduler.py` line 255 |
| NFR-1.5 | Bulk insert articles (100 records/page) | ✅ | `news_repository.py` `execute_values` page_size=100 |
| NFR-1.6 | Bulk upsert prices — loop nhưng commit 1 lần | ⚠️ Mỗi record 1 query | `price_repository.py` line 59-80 — có thể cải thiện bằng `execute_values` |
| NFR-1.7 | LLM request không song song (tránh token rate limit) | ✅ | Synthesis chạy sequential |

### NFR-2. Độ tin cậy (Reliability)

| # | Yêu cầu | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| NFR-2.1 | Retry với exponential backoff cho tất cả external API calls | ✅ | `@retry` (tenacity) khắp nơi |
| NFR-2.2 | Graceful degradation — stream A fail không ảnh hưởng stream B/C | ✅ | try/catch per-symbol, per-stream |
| NFR-2.3 | Per-symbol error isolation trong synthesis | ❌ Bug — re-raises exception | `synthesis_agent.py` line 66 `raise` |
| NFR-2.4 | Pipeline run history tracking (để trace lỗi) | ✅ | `pipeline_runs_repository.py` |
| NFR-2.5 | Dead-letter / requeue không bật — tránh infinite retry loop | ✅ | `message.process(requeue=False)` |

### NFR-3. Khả năng mở rộng (Scalability)

| # | Yêu cầu | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| NFR-3.1 | Container hóa Docker | ✅ | `Dockerfile` tồn tại |
| NFR-3.2 | Scheduler chạy trong process riêng (APScheduler BackgroundScheduler) | ✅ | `scheduler.py` |
| NFR-3.3 | Orchestrator chạy độc lập (RabbitMQ consumer) | ✅ | `orchestrator.py` có thể chạy như service riêng |
| NFR-3.4 | Config qua environment variables | ✅ | `pydantic-settings` + `.env` |

### NFR-4. Giám sát & Quan sát (Observability)

| # | Yêu cầu | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| NFR-4.1 | Structured logging (JSON format) | ⚠️ Basic — chỉ có `logging.basicConfig` | Cần thêm `structlog` hoặc JSON formatter |
| NFR-4.2 | Pipeline run history API (trace lỗi operational) | ✅ | `GET /pipeline/runs`, `GET /pipeline/runs/{id}` |
| NFR-4.3 | SSE progress streaming (debug seed/synthesis) | ✅ | `GET /pipeline/progress` |
| NFR-4.4 | Metrics (Prometheus/OpenTelemetry) | ❌ Chưa có | |
| NFR-4.5 | Distributed tracing (OpenTelemetry) | ❌ Chưa có | |

### NFR-5. Bảo mật (Security)

| # | Yêu cầu | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| NFR-5.1 | API keys trong `.env`, không hard-code | ✅ | |
| NFR-5.2 | Không có sensitive data trong logs | ⚠️ Cần audit | Có thể có symbol names, URLs trong log messages |
| NFR-5.3 | CORS configuration | ⚠️ Chưa thấy trong `main.py` | Cần kiểm tra `app/main.py` |
| NFR-5.4 | Rate limiting trên API endpoints | ❌ Chưa có | |

### NFR-6. Khả năng bảo trì (Maintainability)

| # | Yêu cầu | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| NFR-6.1 | Code có unit tests | ⚠️ Có tests nhưng coverage chưa rõ | Thư mục `tests/` có 11+ test files |
| NFR-6.2 | Tách biệt các concerns (fetch → transform → store) | ✅ | Stream A/B pattern rõ ràng |
| NFR-6.3 | Version control cho DB schema | ⚠️ Có `init.sql` nhưng chưa có migration tool | Nên dùng Alembic |
| NFR-6.4 | API documentation (OpenAPI/Swagger) | ✅ Tự động từ FastAPI | |

---

## III. TÓM TẮT TRẠNG THÁI

### Tổng hợp

| Nhóm | Tổng | ✅ | ⚠️ | ❌ |
|------|------|----|----|-----|
| Nguồn dữ liệu & Thu thập | 19 | 18 | 1 | 0 |
| Làm sạch & Xử lý | 13 | 12 | 1 | 0 |
| Lưu trữ | 12 | 11 | 1 | 0 |
| Tổng hợp AI | 6 | 6 | 0 | 0 |
| Giao tiếp nội bộ | 5 | 5 | 0 | 0 |
| Scheduling | 7 | 6 | 1 | 0 |
| API Quản trị | 18 | 17 | 1 | 0 |
| **NFR** | 19 | 12 | 5 | 2 |
| **Tổng cộng** | **99** | **87 (88%)** | **10 (10%)** | **2 (2%)** |

---

## IV. CÁC ISSUE CẦN ƯU TIÊN SỬA

### P0 — Bug cần fix

1. **`synthesis_agent.py` line 66 re-raises exception** — synthesis per-symbol fail sẽ dừng toàn bộ pipeline. Cần bắt exception, log, tiếp tục symbol tiếp theo (giống như `scheduler.py` `run_synthesis()` đã handle đúng).

### P1 — Cần bổ sung

1. **`pipeline/status` không trả về last_run thực tế** — response hard-code `"status": "idle"`, `"last_run": None`. Nên query `pipeline_runs` bảng gần nhất cho mỗi stream type.

2. **`seed.py` không upsert `eps` field** — khi seed financial_ratios, EPS luôn là NULL vì INSERT statement thiếu `eps` column.

3. **SourceRepository cache invalidation race condition** — `routes.py` toggle source tạo instance mới `SourceRepository().invalidate()` nhưng scheduler có thể đang đọc instance cũ.

### P2 — Cải thiện chất lượng

1. **`price_repository.py` upsert_prices loop per-row** — nên dùng `psycopg2.extras.execute_values` như `news_repository` để bulk upsert.

2. **Nguồn financial ratios không thống nhất (annual vs TTM)** — seed script dùng VnStock/VCI annual ratios, Stream A dùng Yahoo Finance TTM ratios. Seedupsert ghi đè period='annual', Stream A upsert ghi đè period='ttm' vào cùng bảng `financial_ratios`.

3. **Structured logging** — thay `logging.basicConfig` bằng `structlog` với JSON output để dễ parse trong ELK/Datadog.

4. **OpenTelemetry tracing** — thêm distributed tracing cho debug cross-service.

5. **API rate limiting** — bảo vệ `/scripts/seed` và `/synthesis/trigger` khỏi abuse.

6. **DB migration tool** — dùng Alembic thay vì chỉ có `init.sql`.

---

## V. CẤU TRÚC MODULE HIỆN TẠI

```
data-pipeline/
├── app/
│   ├── main.py                     # FastAPI bootstrap + scheduler startup
│   ├── config.py                   # pydantic Settings từ .env
│   ├── scheduler.py                # APScheduler: stream_a / stream_b / synthesis
│   ├── api/
│   │   ├── routes.py              # 15+ endpoints
│   │   └── schemas.py             # Pydantic models + PipelineProgressStore (SSE)
│   ├── sources/
│   │   └── source_repository.py   # DB reads news_sources (5-min cache)
│   ├── pipeline_runs/
│   │   └── pipeline_runs_repository.py  # CRUD pipeline execution history
│   ├── scripts/
│   │   └── seed.py                # CLI: seed VN30 prices/company/ratios/wiki
│   ├── stream_a/                  # Structured data: OHLCV + financial ratios
│   │   ├── fetchers/
│   │   │   ├── base_fetcher.py
│   │   │   ├── vnstock_fetcher.py    # VnStock KBS → OHLCV
│   │   │   └── yahoo_finance_fetcher.py  # Yahoo Finance → TTM ratios
│   │   ├── transformers/
│   │   │   ├── price_transformer.py  # OHLCV validation (0.001–1M, high≥low)
│   │   │   └── ratio_transformer.py  # Ratio validation (P/E≤1000, ROE/ROA any)
│   │   └── repositories/
│   │       └── price_repository.py   # stock_prices + financial_ratios CRUD
│   ├── stream_b/                  # Unstructured: news crawling + embedding
│   │   ├── crawlers/
│   │   │   ├── base_crawler.py
│   │   │   ├── cafef_crawler.py       # Sitemap → 50 articles/30 days
│   │   │   └── vietstock_crawler.py   # Sitemap regex → relative time parse
│   │   ├── transformers/
│   │   │   └── news_transformer.py     # HTML strip + symbol extraction
│   │   ├── repositories/
│   │   │   └── news_repository.py     # news_articles CRUD
│   │   ├── embedder.py                 # Chunk 500c/50o + OpenAI/sentence-transformers
│   │   └── exceptions.py
│   ├── synthesis/                  # AI wiki generation (Karpathy pattern)
│   │   ├── synthesis_agent.py        # Orchestrator: old_wiki + news + prices → LLM
│   │   ├── merger.py                  # LLM prompt + JSON parse + DB override
│   │   ├── wiki_repository.py        # company_wiki CRUD + history
│   │   ├── prompts.py               # System + user prompt templates
│   │   ├── orchestrator.py          # RabbitMQ consumer → triggers synthesis
│   │   └── exceptions.py
│   ├── rabbitmq/
│   │   ├── producer.py              # Publish price.updated + raw.ingested
│   │   └── constants.py
│   └── shared/
│       └── base_transformer.py
├── tests/                         # 11+ test files
├── infra/postgres/
│   └── init.sql                   # Full DB schema (12 tables)
├── Dockerfile
└── requirements.txt
```

---

## VI. DATABASE SCHEMA (12 tables)

| Table | Key | Mục đích |
|-------|-----|---------|
| `stock_prices` | `(symbol, trade_date)` | OHLCV bars |
| `financial_ratios` | `(symbol, period)` | P/E, P/B, EPS, ROE, ROA |
| `news_sources` | `(id)` UUID | Configurable crawlers |
| `news_articles` | `(url)` | Raw crawled articles |
| `company_wiki` | `(symbol)` | Living synthesized wiki |
| `company_wiki_history` | `(symbol, version)` | Append-only version history |
| `company_info` | `(symbol)` | Authoritative metadata from VnStock/VCI |
| `pipeline_runs` | `(id)` UUID | Execution log all streams |
| `pipeline_run_symbols` | `(run_id, symbol)` | Per-symbol results |
| `tracked_symbols` | `(symbol)` | Watchlist |
| `portfolios` | `(user_id)` | Virtual portfolios |
| `holdings` | `(portfolio_id, symbol)` | Positions |
| `transactions` | `(portfolio_id, id)` | Trade log |
| `users` | `(email)` | Accounts |
