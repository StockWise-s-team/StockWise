S D:\HOCTAP\StockWise\data-pipeline> uvicorn app.main:app --host 0.0.0.0 --port 8000
INFO: Started server process [2716]
INFO: Waiting for application startup.
INFO: Application startup complete.
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): [winerror 10048] only one usage of each socket address (protocol/network address/port) is normally permitted
INFO: Waiting for application shutdown.
INFO: Application shutdown complete.
PS D:\HOCTAP\StockWise\data-pipeline> netstat -ano | findstr :8000
TCP 0.0.0.0:8000 0.0.0.0:0 LISTENING 30780
TCP 127.0.0.1:8000 127.0.0.1:50732 FIN_WAIT_2 30780
TCP 127.0.0.1:50732 127.0.0.1:8000 CLOSE_WAIT 22484
PS D:\HOCTAP\StockWise\data-pipeline> taskkill /F /PID 30780
SUCCESS: The process with PID 30780 has been terminated.
PS D:\HOCTAP\StockWise\data-pipeline> taskkill /F /PID 22484
SUCCESS: The process with PID 22484 has been terminated.
PS D:\HOCTAP\StockWise\data-pipeline> uvicorn app.main:app --host 0.0.0.0 --port 8000
INFO: Started server process [7564]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
09:38:54 INFO app.synthesis.synthesis_agent [SynthesisAgent] Starting synthesis for 36 symbols
09:38:55 INFO app.sources.source_repository [SourceRepository] Fetched 2 active sources from DB
09:38:55 INFO app.scheduler [StreamB] Active sources from DB: ['cafef', 'vietstock']
09:38:55 INFO app.scheduler [StreamB] Tracked symbols for priority: ['ACB', 'ADC', 'BID', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG', 'MBB', 'MSN', 'MWG', 'NAB', 'NLG', 'OCB', 'PDR', 'PLX', 'SAB', 'SHB', 'SSB', 'SSI', 'STB', 'TCB', 'TPB', 'VCA', 'VCB', 'VCI', 'VGC', 'VHM', 'VIB', 'VIC', 'VJC', 'VND', 'VNM', 'VPB', 'VRE']
09:38:55 INFO httpx HTTP Request: GET http://localhost:16333 "HTTP/1.1 200 OK"
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ┃
┃ ⚠️ THÔNG BÁO QUAN TRỌNG ┃
┃ ┃
┃ Phát hành vnstock 4.0.1 cung cấp sửa lỗi quan trọng và bổ sung giao diện API ┃
┃ thống nhất (Unified UI), tăng tính ổn định của code. ┃
┃ Cập nhật: pip install vnstock -U ┃
┃ AI Agent Guide: https://github.com/vnstock-hq/vnstock-agent-guide/ ┃
┃ ┃
┃ ────────────────────────────────────────────────────────────────────────────── ┃
┃ ┃
┃ 🚀 VNSTOCK INSIDERS PROGRAM - NÂNG TẦM TRẢI NGHIỆM CỦA BẠN! 🚀 ┃
┃ ┃
┃ Nếu bạn cảm thấy khó chịu với các thông báo và quảng cáo: ┃
┃ ┃
┃ ✨ Ẩn toàn bộ thông báo và quảng cáo phiền hà ┃
┃ 🔓 Mở rộng khả năng sử dụng API tối đa ┃
┃ ⚡ Tăng tốc tải dữ liệu từ 5-8 lần ┃
┃ 📈 Tăng giới hạn truy cập API lên đến 5 lần ┃
┃ 🤖 Dùng AI Agent viết code hiệu quả với tài liệu Agent Guide ┃
┃ ┃
┃ 🔗 Tham gia ngay: https://vnstocks.com/insiders-program#tiers ┃
┃ ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
09:38:57 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=ADC&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:38:57 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=ACB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:38:57 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol ADC: total=447, fetching up to 20
09:38:57 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] ADC: got 1 real articles
09:38:57 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol ACB: total=2629, fetching up to 20
09:38:57 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] ACB: got 3 real articles
09:38:57 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=BID&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:38:57 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol BID: total=1742, fetching up to 20
09:38:57 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] BID: got 3 real articles
09:38:57 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=ADC&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:38:57 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] ADC: got 0 articles (API)
09:38:57 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=ACB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:38:57 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=BID&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:38:57 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 22 bars for ACB
09:38:57 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] BID: got 20 articles (API)
09:38:57 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] ACB: got 20 articles (API)
09:38:58 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for ACB
09:38:58 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 22/22 bars for ACB
09:38:58 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 22 price records
09:38:58 INFO app.scheduler [StreamA] Fetched 22 prices for ACB
09:38:58 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for ACB
09:38:58 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:38:58 INFO app.scheduler [StreamA] Fetched ratios for ACB
09:38:58 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=CTG&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:38:58 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol CTG: total=2572, fetching up to 20
09:38:58 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] CTG: got 3 real articles
09:38:58 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=FPT&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:38:58 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol FPT: total=3948, fetching up to 20
09:38:59 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] FPT: got 11 real articles
09:38:59 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=GAS&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:38:59 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol GAS: total=2876, fetching up to 20
09:38:59 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] GAS: got 7 real articles
09:38:59 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=FPT&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:38:59 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] FPT: got 20 articles (API)
09:38:59 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=GAS&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:38:59 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=CTG&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:38:59 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] CTG: got 20 articles (API)
09:38:59 INFO app.stream_c.runner [StreamC] Published 36/36 symbols via vnstock_price_board to market.exchange/price.updated
09:38:59 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run f9d6017a-0693-45d4-97d4-203f576fb5c4 with status=success
09:39:00 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=GAS&resourceCode=0&type=latest&reportType=0&pageIndex=2&pageSize=20 "HTTP/1.1 200 OK"
09:39:00 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] GAS: got 20 articles (API)
09:39:00 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=HPG&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:00 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol HPG: total=2822, fetching up to 20
09:39:00 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] HPG: got 2 real articles
09:39:00 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=HDB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:00 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol HDB: total=2287, fetching up to 20
09:39:00 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] HDB: got 7 real articles
09:39:00 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=GVR&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:00 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol GVR: total=584, fetching up to 20
09:39:00 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] GVR: got 8 real articles
09:39:00 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=GVR&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:00 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] GVR: got 20 articles (API)
09:39:00 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=HDB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:01 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] HDB: got 20 articles (API)
09:39:02 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=MSN&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:02 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol MSN: total=2695, fetching up to 20
09:39:02 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] MSN: got 6 real articles
09:39:02 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=MBB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:02 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=MWG&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:02 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol MBB: total=3315, fetching up to 20
09:39:02 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] MBB: got 7 real articles
09:39:02 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol MWG: total=2410, fetching up to 20
09:39:02 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] MWG: got 6 real articles
09:39:02 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=HPG&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:02 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] HPG: got 20 articles (API)
09:39:02 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=MBB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:02 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=MSN&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:02 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] MSN: got 20 articles (API)
09:39:02 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=MBB&resourceCode=0&type=latest&reportType=0&pageIndex=2&pageSize=20 "HTTP/1.1 200 OK"
09:39:02 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] MBB: got 20 articles (API)
09:39:03 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 3 bars for ADC
09:39:03 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for ADC
09:39:03 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 3/3 bars for ADC
09:39:03 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 3 price records
09:39:03 INFO app.scheduler [StreamA] Fetched 3 prices for ADC
09:39:03 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for ADC
09:39:03 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:03 INFO app.scheduler [StreamA] Fetched ratios for ADC
09:39:03 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=NAB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:03 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol NAB: total=673, fetching up to 20
09:39:03 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] NAB: got 2 real articles
09:39:03 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=OCB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:03 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=NLG&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:03 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol OCB: total=1343, fetching up to 20
09:39:03 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] OCB: got 14 real articles
09:39:03 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol NLG: total=2560, fetching up to 20
09:39:03 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] NLG: got 16 real articles
09:39:03 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=MWG&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:03 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=NLG&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:03 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] MWG: got 20 articles (API)
09:39:04 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=NAB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:04 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] NAB: got 20 articles (API)
09:39:04 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=NLG&resourceCode=0&type=latest&reportType=0&pageIndex=2&pageSize=20 "HTTP/1.1 200 OK"
09:39:04 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] NLG: got 20 articles (API)
09:39:05 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=PLX&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:05 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol PLX: total=812, fetching up to 20
09:39:05 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] PLX: got 6 real articles
09:39:05 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=SAB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:05 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=PDR&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:05 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol SAB: total=845, fetching up to 20
09:39:05 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] SAB: got 3 real articles
09:39:05 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol PDR: total=1968, fetching up to 20
09:39:05 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] PDR: got 9 real articles
09:39:05 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=PLX&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:05 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=PDR&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:05 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] PLX: got 20 articles (API)
09:39:05 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=OCB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:05 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] PDR: got 20 articles (API)
09:39:05 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] OCB: got 20 articles (API)
09:39:06 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=SSB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:06 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol SSB: total=1196, fetching up to 20
09:39:06 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] SSB: got 3 real articles
09:39:06 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=SSI&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:06 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol SSI: total=5282, fetching up to 20
09:39:06 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] SSI: got 2 real articles
09:39:06 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=SHB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:06 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol SHB: total=2380, fetching up to 20
09:39:06 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] SHB: got 4 real articles
09:39:07 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=SAB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:07 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=SSB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:07 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] SSB: got 8 articles (API)
09:39:07 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=SHB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:07 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] SHB: got 20 articles (API)
09:39:07 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=SAB&resourceCode=0&type=latest&reportType=0&pageIndex=2&pageSize=20 "HTTP/1.1 200 OK"
09:39:08 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for BID
09:39:08 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] SAB: got 20 articles (API)
09:39:08 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=STB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:08 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol STB: total=3636, fetching up to 20
09:39:08 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] STB: got 0 real articles
09:39:08 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=TCB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:08 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol TCB: total=2258, fetching up to 20
09:39:08 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] TCB: got 8 real articles
09:39:08 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=TPB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:08 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol TPB: total=1362, fetching up to 20
09:39:08 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] TPB: got 14 real articles
09:39:08 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for BID
09:39:08 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for BID
09:39:08 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=STB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:08 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:08 INFO app.scheduler [StreamA] Fetched 21 prices for BID
09:39:08 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for BID
09:39:08 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:08 INFO app.scheduler [StreamA] Fetched ratios for BID
09:39:09 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=SSI&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:09 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] SSI: got 20 articles (API)
09:39:09 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VCA&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:09 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VCA: total=434, fetching up to 20
09:39:09 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VCA: got 0 real articles
09:39:09 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VCB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:09 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VCI&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:09 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VCB: total=2287, fetching up to 20
09:39:09 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VCB: got 3 real articles
09:39:09 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VCI: total=1042, fetching up to 20
09:39:09 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VCI: got 3 real articles
09:39:09 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=STB&resourceCode=0&type=latest&reportType=0&pageIndex=2&pageSize=20 "HTTP/1.1 200 OK"
09:39:09 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] STB: got 20 articles (API)
09:39:09 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=TCB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:10 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] TCB: got 20 articles (API)
09:39:11 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VGC&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:11 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VGC: total=794, fetching up to 20
09:39:11 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VGC: got 3 real articles
09:39:11 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VHM&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:11 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VIB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:11 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VIB: total=2016, fetching up to 20
09:39:11 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VIB: got 9 real articles
09:39:11 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VHM: total=1355, fetching up to 20
09:39:11 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VHM: got 5 real articles
09:39:11 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=TPB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:11 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VCA&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:11 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VCA: got 0 articles (API)
09:39:11 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] TPB: got 20 articles (API)
09:39:12 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VND&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:12 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VJC&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:12 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VIC&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:12 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VJC: total=1351, fetching up to 20
09:39:12 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VJC: got 7 real articles
09:39:12 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VND: total=4465, fetching up to 20
09:39:12 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VND: got 7 real articles
09:39:12 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VIC: total=3559, fetching up to 20
09:39:12 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VIC: got 8 real articles
09:39:12 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VCB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:12 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VCB: got 20 articles (API)
09:39:12 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VGC&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:13 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VCI&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:13 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VGC: got 20 articles (API)
09:39:13 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VCI: got 20 articles (API)
09:39:13 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for CTG
09:39:13 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for CTG
09:39:13 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for CTG
09:39:13 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:13 INFO app.scheduler [StreamA] Fetched 21 prices for CTG
09:39:13 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for CTG
09:39:13 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:13 INFO app.scheduler [StreamA] Fetched ratios for CTG
09:39:14 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VNM&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:14 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VRE&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:14 INFO httpx HTTP Request: POST https://dc.vietstock.vn/api/Search/SearchArticleNewAsync?keySearch=VPB&currentPage=1&pageSize=20&skip=0&filterTime=all "HTTP/1.1 200 OK"
09:39:14 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VPB: total=2149, fetching up to 20
09:39:14 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VPB: got 10 real articles
09:39:14 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VNM: total=4241, fetching up to 20
09:39:14 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VNM: got 9 real articles
09:39:14 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Symbol VRE: total=873, fetching up to 20
09:39:14 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] VRE: got 4 real articles
09:39:14 INFO app.stream_b.crawlers.vietstock_crawler [VietstockCrawler] Total unique articles: 138 (from 36 symbols)
09:39:14 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VIB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:14 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VHM&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:14 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VIC&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:14 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VIB: got 20 articles (API)
09:39:14 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VHM: got 20 articles (API)
09:39:15 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VIC&resourceCode=0&type=latest&reportType=0&pageIndex=2&pageSize=20 "HTTP/1.1 200 OK"
09:39:15 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VIC: got 20 articles (API)
09:39:16 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VJC&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:16 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VND&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:16 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VJC: got 20 articles (API)
09:39:16 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VND: got 20 articles (API)
09:39:16 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VNM&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:16 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VNM: got 20 articles (API)
09:39:17 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VRE&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:17 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VRE: got 20 articles (API)
09:39:17 INFO httpx HTTP Request: GET https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach?symbol=VPB&resourceCode=0&type=latest&reportType=0&pageIndex=1&pageSize=20 "HTTP/1.1 200 OK"
09:39:17 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] VPB: got 20 articles (API)
09:39:17 INFO app.stream_b.crawlers.cafef_crawler [CafeFCrawler] Total unique articles: 603 (from 36 symbols)
09:39:17 INFO app.scheduler [StreamB] cafef returned 603 articles
09:39:17 INFO app.scheduler [StreamB] vietstock returned 138 articles
09:39:17 INFO app.shared.ticker_validator [TickerValidator] Loaded 1565 valid tickers from D:\HOCTAP\StockWise\data-pipeline\valid_tickers.json
The input looks more like a filename than markup. You may want to open this file and pass the filehandle into Beautiful Soup.
09:39:18 INFO app.stream_b.repositories.news_repository [NewsRepository] Bulk inserted 0 articles
09:39:18 INFO app.scheduler [StreamB] Inserted 0 articles into DB
09:39:18 INFO httpx HTTP Request: GET http://localhost:16333/collections/news_chunks "HTTP/1.1 200 OK"
09:39:18 INFO app.stream_b.embedder [Embedder] Collection 'news_chunks' already exists
09:39:18 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for FPT
09:39:18 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for FPT
09:39:18 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for FPT
09:39:19 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:19 INFO app.scheduler [StreamA] Fetched 21 prices for FPT
09:39:19 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for FPT
09:39:19 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:19 INFO app.scheduler [StreamA] Fetched ratios for FPT
09:39:22 INFO httpx HTTP Request: POST https://luongchidung.online/v1/chat/completions "HTTP/1.1 200 OK"
09:39:22 INFO app.synthesis.wiki_repository [WikiRepository] Upserted wiki for ACB (version 51)
09:39:22 INFO app.synthesis.synthesis_agent [SynthesisAgent] Completed synthesis for ACB (v51)
09:39:23 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for GAS
09:39:24 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for GAS
09:39:24 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for GAS
09:39:24 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:24 INFO app.scheduler [StreamA] Fetched 21 prices for GAS
09:39:24 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for GAS
09:39:24 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:24 INFO app.scheduler [StreamA] Fetched ratios for GAS
09:39:25 INFO sentence_transformers.base.model No device provided, using cpu
09:39:26 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/modules.json "HTTP/1.1 307 Temporary Redirect"
09:39:26 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/modules.json "HTTP/1.1 200 OK"
09:39:26 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config_sentence_transformers.json "HTTP/1.1 307 Temporary Redirect"
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
09:39:26 WARNING huggingface_hub.utils.\_http Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
09:39:26 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config_sentence_transformers.json "HTTP/1.1 200 OK"
09:39:26 INFO sentence_transformers.base.model Loading SentenceTransformer model from sentence-transformers/all-MiniLM-L6-v2.
09:39:26 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config_sentence_transformers.json "HTTP/1.1 307 Temporary Redirect"
09:39:26 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config_sentence_transformers.json "HTTP/1.1 200 OK"
09:39:27 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/README.md "HTTP/1.1 307 Temporary Redirect"
09:39:27 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/README.md "HTTP/1.1 200 OK"
09:39:27 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/modules.json "HTTP/1.1 307 Temporary Redirect"
09:39:27 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/modules.json "HTTP/1.1 200 OK"
09:39:28 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/sentence_bert_config.json "HTTP/1.1 307 Temporary Redirect"
09:39:28 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/sentence_bert_config.json "HTTP/1.1 200 OK"
09:39:28 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/adapter_config.json "HTTP/1.1 404 Not Found"
09:39:28 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
09:39:28 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config.json "HTTP/1.1 200 OK"
Loading weights: 100%|█████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 7353.92it/s]
09:39:29 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
09:39:29 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for GVR
09:39:29 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for GVR
09:39:29 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for GVR
09:39:29 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 404 Not Found"
09:39:29 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:29 INFO app.scheduler [StreamA] Fetched 21 prices for GVR
09:39:29 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for GVR
09:39:29 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:29 INFO app.scheduler [StreamA] Fetched ratios for GVR
09:39:29 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/video_preprocessor_config.json "HTTP/1.1 404 Not Found"
09:39:29 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 404 Not Found"
09:39:29 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Created run 40d261ac-6eba-495d-ae80-017677d5f216 (type=stream_c, trigger=continuous)
09:39:29 INFO app.stream_c.runner [StreamC] Fetching via vnstock (primary) for 36 symbols
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/tokenizer_config.json "HTTP/1.1 200 OK"
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config.json "HTTP/1.1 200 OK"
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config.json "HTTP/1.1 200 OK"
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
09:39:30 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/tokenizer_config.json "HTTP/1.1 200 OK"
09:39:31 INFO httpx HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2/tree/main/additional_chat_templates?recursive=false&expand=false "HTTP/1.1 404 Not Found"
09:39:31 INFO app.stream_c.runner [StreamC] Published 36/36 symbols via vnstock_price_board to market.exchange/price.updated
09:39:31 INFO httpx HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2/tree/main?recursive=true&expand=false "HTTP/1.1 200 OK"
09:39:31 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run 40d261ac-6eba-495d-ae80-017677d5f216 with status=success
09:39:31 INFO httpx HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/1_Pooling/config.json "HTTP/1.1 307 Temporary Redirect"
09:39:31 INFO httpx HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/1_Pooling%2Fconfig.json "HTTP/1.1 200 OK"
09:39:32 INFO httpx HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2 "HTTP/1.1 200 OK"
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.02it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 48.75it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 33.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.75it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 33.96it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 27.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.06it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.68it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.46it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 87.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.93it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 24.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 49.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.28it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.41it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 89.76it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.99it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 108.83it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 119.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 76.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.02it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 31.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 33.41it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:34 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for HDB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.88it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 65.82it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 70.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.76it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 64.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 75.99it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:34 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for HDB
09:39:34 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for HDB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.74it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:34 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:34 INFO app.scheduler [StreamA] Fetched 21 prices for HDB
09:39:34 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for HDB
09:39:34 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:34 INFO app.scheduler [StreamA] Fetched ratios for HDB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.46it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 29.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 64.41it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 33.30it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.96it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 70.46it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.50it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 29.31it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.63it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.34it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.48it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 28.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.31it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.38it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 24.47it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.01it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 74.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 52.75it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 79.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 31.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 73.30it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 78.82it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 77.71it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 100.85it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 104.11it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 133.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 76.69it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 103.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 89.29it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.42it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 113.08it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 103.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 71.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.28it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 100.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.20it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 40.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.02it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 74.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.29it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.27it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.39it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 40.63it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.90it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.50it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 33.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.34it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.99it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.80it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.90it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.56it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.88it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.94it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.67it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.64it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 49.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 31.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 52.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 70.50it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.93it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 29.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 69.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.73it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 31.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.60it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.92it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 29.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.22it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 127.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.47it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 70.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 90.47it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 48.76it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.75it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.84it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.64it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.48it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.35it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.42it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 28.17it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.63it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.57it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:39 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for HPG
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.59it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 69.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 65.65it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.83it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.07it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 86.26it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 102.92it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 31.33it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:39 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for HPG
09:39:39 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for HPG
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.10it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:39 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:39 INFO app.scheduler [StreamA] Fetched 21 prices for HPG
09:39:39 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for HPG
09:39:39 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.77it/s]09:39:39 INFO app.scheduler [StreamA] Fetched ratios for HPG

Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 25.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 28.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.28it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.20it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.38it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.31it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.54it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.27it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.06it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 87.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.34it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 101.60it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 119.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.20it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 88.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 96.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 94.51it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 101.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 49.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 75.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.90it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.38it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.40it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 40.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.41it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.07it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.81it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.96it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 24.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 84.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.72it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.88it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 91.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 83.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 73.93it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 113.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 96.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 92.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.46it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 93.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 40.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.42it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 23.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.40it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 66.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 73.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 66.48it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 96.60it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 80.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 72.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 77.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 80.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 29.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 27.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.17it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.54it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 23.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 67.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 80.90it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 64.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.87it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 106.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 94.11it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 112.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.89it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 126.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.74it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 100.38it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.60it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 98.48it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 70.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.63it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 52.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.35it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.06it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.80it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 117.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 93.40it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 94.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 91.67it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 97.90it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 88.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.76it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.68it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 104.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 98.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 89.48it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.92it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 31.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.75it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.64it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 40.82it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 64.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 20.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.17it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 52.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.41it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.31it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.93it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 77.17it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.54it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 84.98it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 84.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 98.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.70it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:44 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for MBB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 29.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.18it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.85it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 39.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 28.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.85it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.16it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:45 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for MBB
09:39:45 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for MBB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.92it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:45 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:45 INFO app.scheduler [StreamA] Fetched 21 prices for MBB
09:39:45 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for MBB
09:39:45 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:45 INFO app.scheduler [StreamA] Fetched ratios for MBB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.12it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 25.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.39it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.12it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 99.30it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 75.75it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 74.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 39.41it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 76.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 90.11it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 110.93it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 89.07it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 77.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 33.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 42.81it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 40.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 23.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 67.81it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 39.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.81it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 32.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 38.90it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 83.12it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 71.88it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 89.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 99.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 83.50it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 94.80it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 69.38it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.56it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.39it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 38.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.67it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 78.30it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 88.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 89.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.54it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 74.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 98.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 80.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 82.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 97.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 95.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 97.78it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.88it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.54it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 25.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 25.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 35.28it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 25.85it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.34it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 83.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 85.76it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 80.40it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 132.12it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.39it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.17it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.41it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.39it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 83.76it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 86.64it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 99.60it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 88.35it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 97.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 87.84it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 88.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 92.95it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 121.67it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 88.80it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.11it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 112.76it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.67it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 105.35it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 74.07it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 92.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 94.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.42it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 91.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 38.40it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 67.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 79.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 48.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.07it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.21it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 86.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.20it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.73it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.48it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.82it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 39.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.68it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 91.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 76.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 64.82it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:49 INFO httpx HTTP Request: POST https://luongchidung.online/v1/chat/completions "HTTP/1.1 200 OK"
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 69.56it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:49 INFO app.synthesis.wiki_repository [WikiRepository] Upserted wiki for ADC (version 52)
09:39:49 INFO app.synthesis.synthesis_agent [SynthesisAgent] Completed synthesis for ADC (v52)
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.30it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 24.33it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:50 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for MSN
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.63it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:50 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for MSN
09:39:50 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for MSN
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 33.58it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:50 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:50 INFO app.scheduler [StreamA] Fetched 21 prices for MSN
09:39:50 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for MSN
09:39:50 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:50 INFO app.scheduler [StreamA] Fetched ratios for MSN
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.42it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.75it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 34.01it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 28.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 25.83it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 29.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 39.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 23.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 24.48it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.59it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.41it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.54it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.67it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 30.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.27it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.84it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 23.78it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.56it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 28.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.99it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.96it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.24it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 19.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 37.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 18.93it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.47it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 22.84it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 67.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 49.89it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.39it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.58it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.99it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.52it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.59it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.35it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.74it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:56 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for MWG
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.75it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.96it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:39:56 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for MWG
09:39:56 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for MWG
09:39:56 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:39:56 INFO app.scheduler [StreamA] Fetched 21 prices for MWG
09:39:56 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for MWG
09:39:56 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:39:56 INFO app.scheduler [StreamA] Fetched ratios for MWG
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.12it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.17it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.00it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.78it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.83it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.02it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.85it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.80it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.35it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.56it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.11it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:01 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for NAB
09:40:01 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Created run 230c466e-4192-4f61-9a3b-84a9375e8a36 (type=stream_c, trigger=continuous)
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.01it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:01 INFO app.stream_c.runner [StreamC] Fetching via vnstock (primary) for 36 symbols
09:40:01 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for NAB
09:40:01 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for NAB
09:40:01 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:01 INFO app.scheduler [StreamA] Fetched 21 prices for NAB
09:40:01 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for NAB
09:40:01 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:01 INFO app.scheduler [StreamA] Fetched ratios for NAB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.78it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.99it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.27it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.93it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.04it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:03 INFO app.stream_c.runner [StreamC] Published 36/36 symbols via vnstock_price_board to market.exchange/price.updated
09:40:03 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run 230c466e-4192-4f61-9a3b-84a9375e8a36 with status=success
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.73it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.85it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.30it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.34it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.15it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.96it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:06 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 22 bars for NLG
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.42it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:06 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for NLG
09:40:06 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 22/22 bars for NLG
09:40:06 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 22 price records
09:40:06 INFO app.scheduler [StreamA] Fetched 22 prices for NLG
09:40:06 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for NLG
09:40:06 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:06 INFO app.scheduler [StreamA] Fetched ratios for NLG
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.73it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.28it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.02it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.44it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.60it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.69it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.43it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:11 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for OCB
09:40:11 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for OCB
09:40:11 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for OCB
09:40:12 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:12 INFO app.scheduler [StreamA] Fetched 21 prices for OCB
09:40:12 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for OCB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.49it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:12 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:12 INFO app.scheduler [StreamA] Fetched ratios for OCB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.40it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.98it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.45it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.50it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.40it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:01<00:00, 1.90it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.77it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:16 INFO httpx HTTP Request: POST https://luongchidung.online/v1/chat/completions "HTTP/1.1 200 OK"
09:40:16 ERROR app.synthesis.merger [Merger] Invalid JSON from LLM for BID: Expecting value: line 1 column 1 (char 0)
09:40:16 ERROR app.synthesis.synthesis_agent [SynthesisAgent] Failed to synthesize BID: LLMParseError: Invalid JSON for BID: Expecting value: line 1 column 1 (char 0)
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.56it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.07it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.59it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:17 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for PDR
09:40:17 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for PDR
09:40:17 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for PDR
09:40:17 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:17 INFO app.scheduler [StreamA] Fetched 21 prices for PDR
09:40:17 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for PDR
09:40:17 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:17 INFO app.scheduler [StreamA] Fetched ratios for PDR
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.93it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.56it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.01it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 9.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.82it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.73it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.78it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.16it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.02it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.11it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:22 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for PLX
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.18it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.79it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:22 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for PLX
09:40:22 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for PLX
09:40:22 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:22 INFO app.scheduler [StreamA] Fetched 21 prices for PLX
09:40:22 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for PLX
09:40:22 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:22 INFO app.scheduler [StreamA] Fetched ratios for PLX
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.82it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 23.47it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.92it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 7.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.04it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.96it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.68it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 4.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 3.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.95it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.12it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.83it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.33it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:27 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for SAB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.94it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.31it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:28 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for SAB
09:40:28 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for SAB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 6.37it/s]
Batches: 0%| | 0/1 [00:00<?, ?it/s]09:40:28 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:28 INFO app.scheduler [StreamA] Fetched 21 prices for SAB
09:40:28 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for SAB
09:40:28 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:28 INFO app.scheduler [StreamA] Fetched ratios for SAB
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.18it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.07it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 8.83it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:01<00:00, 1.66it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 5.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 2.59it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1.96it/s]
09:40:32 INFO httpx HTTP Request: PUT http://localhost:16333/collections/news_chunks/points?wait=true "HTTP/1.1 200 OK"
09:40:32 INFO app.stream_b.embedder [Embedder] Upserted 2042 chunks (741 articles)
09:40:32 INFO app.scheduler [StreamB] Embedded 2042 chunks into Qdrant
09:40:32 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run 8c81ac4e-85d4-41c9-8dfe-30512504b59b with status=success
09:40:33 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for SHB
09:40:33 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for SHB
09:40:33 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for SHB
09:40:33 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:33 INFO app.scheduler [StreamA] Fetched 21 prices for SHB
09:40:33 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for SHB
09:40:33 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:33 INFO app.scheduler [StreamA] Fetched ratios for SHB
09:40:33 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Created run 55ed190b-e98b-4243-9e19-8a61786bfe42 (type=stream_c, trigger=continuous)
09:40:33 INFO app.stream_c.runner [StreamC] Fetching via vnstock (primary) for 36 symbols
09:40:35 INFO app.stream_c.runner [StreamC] Published 36/36 symbols via vnstock_price_board to market.exchange/price.updated
09:40:35 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run 55ed190b-e98b-4243-9e19-8a61786bfe42 with status=success
09:40:38 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for SSB
09:40:38 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for SSB
09:40:38 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for SSB
09:40:38 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:38 INFO app.scheduler [StreamA] Fetched 21 prices for SSB
09:40:38 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for SSB
09:40:38 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:38 INFO app.scheduler [StreamA] Fetched ratios for SSB
09:40:43 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for SSI
09:40:44 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for SSI
09:40:44 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for SSI
09:40:44 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:44 INFO app.scheduler [StreamA] Fetched 21 prices for SSI
09:40:44 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for SSI
09:40:44 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:44 INFO app.scheduler [StreamA] Fetched ratios for SSI
09:40:45 INFO httpx HTTP Request: POST https://luongchidung.online/v1/chat/completions "HTTP/1.1 200 OK"
09:40:45 INFO app.synthesis.wiki_repository [WikiRepository] Upserted wiki for CTG (version 49)
09:40:45 INFO app.synthesis.synthesis_agent [SynthesisAgent] Completed synthesis for CTG (v49)
09:40:49 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for STB
09:40:49 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for STB
09:40:49 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for STB
09:40:49 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:49 INFO app.scheduler [StreamA] Fetched 21 prices for STB
09:40:49 WARNING app.stream_a.transformers.ratio_transformer [RatioTransformer] Skipped invalid ratios for STB: 'eps' must be non-negative, got -163.07
09:40:49 INFO app.scheduler [StreamA] Fetched ratios for STB
09:40:54 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for TCB
09:40:54 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for TCB
09:40:54 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for TCB
09:40:54 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:54 INFO app.scheduler [StreamA] Fetched 21 prices for TCB
09:40:54 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for TCB
09:40:54 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:54 INFO app.scheduler [StreamA] Fetched ratios for TCB
09:40:59 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for TPB
09:40:59 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for TPB
09:40:59 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for TPB
09:40:59 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:40:59 INFO app.scheduler [StreamA] Fetched 21 prices for TPB
09:40:59 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for TPB
09:40:59 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:40:59 INFO app.scheduler [StreamA] Fetched ratios for TPB
09:41:04 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 17 bars for VCA
09:41:05 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VCA
09:41:05 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 17/17 bars for VCA
09:41:05 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 17 price records
09:41:05 INFO app.scheduler [StreamA] Fetched 17 prices for VCA
09:41:05 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VCA
09:41:05 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:05 INFO app.scheduler [StreamA] Fetched ratios for VCA
09:41:05 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Created run 9e271271-77a9-4f5e-937a-cd4ff6f67bfb (type=stream_c, trigger=continuous)
09:41:05 INFO app.stream_c.runner [StreamC] Fetching via vnstock (primary) for 36 symbols
09:41:07 INFO app.stream_c.runner [StreamC] Published 36/36 symbols via vnstock_price_board to market.exchange/price.updated
09:41:07 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run 9e271271-77a9-4f5e-937a-cd4ff6f67bfb with status=success
09:41:10 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VCB
09:41:10 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VCB
09:41:10 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VCB
09:41:10 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:10 INFO app.scheduler [StreamA] Fetched 21 prices for VCB
09:41:10 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VCB
09:41:10 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:10 INFO app.scheduler [StreamA] Fetched ratios for VCB
09:41:15 INFO httpx HTTP Request: POST https://luongchidung.online/v1/chat/completions "HTTP/1.1 200 OK"
09:41:15 INFO app.synthesis.wiki_repository [WikiRepository] Upserted wiki for FPT (version 15)
09:41:15 INFO app.synthesis.synthesis_agent [SynthesisAgent] Completed synthesis for FPT (v15)
09:41:16 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VCI
09:41:16 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VCI
09:41:16 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VCI
09:41:16 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:16 INFO app.scheduler [StreamA] Fetched 21 prices for VCI
09:41:16 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VCI
09:41:16 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:16 INFO app.scheduler [StreamA] Fetched ratios for VCI
09:41:21 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VGC
09:41:21 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VGC
09:41:21 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VGC
09:41:21 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:21 INFO app.scheduler [StreamA] Fetched 21 prices for VGC
09:41:21 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VGC
09:41:21 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:21 INFO app.scheduler [StreamA] Fetched ratios for VGC
09:41:26 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VHM
09:41:26 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VHM
09:41:26 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VHM
09:41:26 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:26 INFO app.scheduler [StreamA] Fetched 21 prices for VHM
09:41:26 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VHM
09:41:26 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:26 INFO app.scheduler [StreamA] Fetched ratios for VHM
09:41:31 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VIB
09:41:31 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VIB
09:41:31 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VIB
09:41:31 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:31 INFO app.scheduler [StreamA] Fetched 21 prices for VIB
09:41:31 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VIB
09:41:31 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:31 INFO app.scheduler [StreamA] Fetched ratios for VIB
09:41:36 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VIC
09:41:37 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VIC
09:41:37 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VIC
09:41:37 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:37 INFO app.scheduler [StreamA] Fetched 21 prices for VIC
09:41:37 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VIC
09:41:37 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:37 INFO app.scheduler [StreamA] Fetched ratios for VIC
09:41:38 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Created run e3d769cc-9750-478a-b129-8b52fd0e32f7 (type=stream_c, trigger=continuous)
09:41:38 INFO app.stream_c.runner [StreamC] Fetching via vnstock (primary) for 36 symbols
09:41:39 INFO app.stream_c.runner [StreamC] Published 36/36 symbols via vnstock_price_board to market.exchange/price.updated
09:41:39 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run e3d769cc-9750-478a-b129-8b52fd0e32f7 with status=success
09:41:41 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VJC
09:41:42 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VJC
09:41:42 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VJC
09:41:42 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:42 INFO app.scheduler [StreamA] Fetched 21 prices for VJC
09:41:42 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VJC
09:41:42 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:42 INFO app.scheduler [StreamA] Fetched ratios for VJC
09:41:42 INFO httpx HTTP Request: POST https://luongchidung.online/v1/chat/completions "HTTP/1.1 200 OK"
09:41:42 INFO app.synthesis.wiki_repository [WikiRepository] Upserted wiki for GAS (version 48)
09:41:42 INFO app.synthesis.synthesis_agent [SynthesisAgent] Completed synthesis for GAS (v48)
09:41:46 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VND
09:41:47 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VND
09:41:47 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VND
09:41:47 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:47 INFO app.scheduler [StreamA] Fetched 21 prices for VND
09:41:47 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VND
09:41:47 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:47 INFO app.scheduler [StreamA] Fetched ratios for VND
09:41:52 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VNM
09:41:52 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VNM
09:41:52 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VNM
09:41:52 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:52 INFO app.scheduler [StreamA] Fetched 21 prices for VNM
09:41:52 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VNM
09:41:52 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:52 INFO app.scheduler [StreamA] Fetched ratios for VNM
09:41:57 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VPB
09:41:58 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VPB
09:41:58 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VPB
09:41:58 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:41:58 INFO app.scheduler [StreamA] Fetched 21 prices for VPB
09:41:58 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VPB
09:41:58 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:41:58 INFO app.scheduler [StreamA] Fetched ratios for VPB
09:42:02 INFO app.stream_a.fetchers.vnstock_fetcher [VnStockFetcher] Fetched 21 bars for VRE
09:42:03 INFO app.stream_a.fetchers.yahoo_finance_fetcher [YahooFinanceFetcher] Fetched ratios for VRE
09:42:03 INFO app.stream_a.transformers.price_transformer [PriceTransformer] Transformed 21/21 bars for VRE
09:42:03 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 21 price records
09:42:03 INFO app.scheduler [StreamA] Fetched 21 prices for VRE
09:42:03 INFO app.stream_a.transformers.ratio_transformer [RatioTransformer] Transformed ratios for VRE
09:42:03 INFO app.stream_a.repositories.price_repository [PriceRepository] Upserted 1 ratio records
09:42:03 INFO app.scheduler [StreamA] Fetched ratios for VRE
09:42:03 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run 0066266e-0bf8-4d4b-9f1d-af3f64cce69f with status=success
09:42:08 INFO httpx HTTP Request: POST https://luongchidung.online/v1/chat/completions "HTTP/1.1 200 OK"
09:42:08 INFO app.synthesis.wiki_repository [WikiRepository] Upserted wiki for GVR (version 47)
09:42:08 INFO app.synthesis.synthesis_agent [SynthesisAgent] Completed synthesis for GVR (v47)
09:42:09 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Created run 884e6902-b60f-4955-9347-918a42977608 (type=stream_c, trigger=continuous)
09:42:09 INFO app.stream_c.runner [StreamC] Fetching via vnstock (primary) for 36 symbols
09:42:12 INFO app.stream_c.runner [StreamC] Published 36/36 symbols via vnstock_price_board to market.exchange/price.updated
09:42:12 INFO app.pipeline_runs.pipeline_runs_repository [PipelineRuns] Finished run 884e6902-b60f-4955-9347-918a42977608 with status=success
