# Market Service — Implementation Plan

## Mục tiêu triển khai

Biến `market-service` từ một service trả mock data thành một market read API thực sự, dựa trên dữ liệu đã được ingest và chuẩn hóa trong PostgreSQL.

Mục tiêu cụ thể:
- query dữ liệu thật từ `stock_prices` và `financial_ratios`
- chuẩn hóa contract API bằng DTO
- validate input rõ ràng
- trả error code nhất quán
- xác định rõ vai trò RabbitMQ consumer
- sẵn sàng cho frontend dashboard/chart tích hợp

## Nguyên tắc kiến trúc

### 1. Không fetch trực tiếp từ nguồn ngoài trong market-service
`data-pipeline` đã là nơi tích hợp external providers (`vnstock`, Yahoo Finance, crawlers). `market-service` nên tránh lặp lại logic fetch để không gây:
- duplicated source logic
- dữ liệu lệch giữa các service
- retry/rate-limit xử lý phân tán

### 2. Market-service là read/query layer
Service này nên tập trung vào:
- query PostgreSQL
- mapping sang DTO
- response nhanh và ổn định
- optional cache/freshness handling nếu cần

### 3. RabbitMQ consumer là event hook, không phải writer chính
Với payload hiện tại của `price.updated`, consumer hợp lý hơn cho:
- log
- invalidate cache
- metrics hoặc freshness timestamp

Không nên phụ thuộc vào consumer này để ghi `stock_prices`, vì dữ liệu thật đang được `data-pipeline` ghi trực tiếp vào DB.

## Kế hoạch triển khai theo bước

## Phase 1 — Thay mock data bằng truy vấn DB thật

### Việc cần làm
1. Inject `StockPriceRepository` và `FinancialRatioRepository` vào `MarketService`.
2. Chuẩn hóa `symbol` bằng `trim().toUpperCase()` trước khi query.
3. Implement `getLatestPrice(symbol)` bằng truy vấn 2 bản ghi mới nhất.
4. Implement `getOhlc(symbol, startDate, endDate)` bằng truy vấn range thật.
5. Implement `getRatios(symbol)` bằng `FinancialRatioRepository`.

### Gợi ý thay đổi repository
`StockPriceRepository` hiện chưa có method lấy latest record. Có thể bổ sung:

```java
Optional<StockPrice> findTopBySymbolOrderByTradeDateDesc(String symbol);
List<StockPrice> findTop2BySymbolOrderByTradeDateDesc(String symbol);
List<StockPrice> findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(String symbol, LocalDate start, LocalDate end);
```

Với `FinancialRatioRepository`, có thể bổ sung sort rõ hơn nếu cần:

```java
List<FinancialRatio> findBySymbolOrderByPeriodDesc(String symbol);
```

### Definition of done cho phase 1
- endpoint trả dữ liệu DB thật
- không còn hardcoded values trong `MarketService`
- symbol không phân biệt hoa thường
- trường hợp không có dữ liệu được xử lý rõ ràng

## Phase 2 — Tách DTO khỏi entity

### Việc cần làm
1. Tạo package DTO riêng, ví dụ:
   - `adapter/in/web/dto/LatestPriceResponse.java`
   - `adapter/in/web/dto/OhlcSeriesResponse.java`
   - `adapter/in/web/dto/FinancialRatioListResponse.java`
2. Tạo mapper từ entity sang DTO.
3. Sửa controller để trả DTO thay vì entity.

### Tại sao phải làm bước này
- giảm coupling giữa DB schema và API shape
- cho phép rename field phù hợp với frontend (`date` thay vì `tradeDate` ở OHLC series)
- thêm field tính toán như `change`, `changePercent` mà không ép entity thay đổi

### Definition of done cho phase 2
- controller không trả JPA entity trực tiếp
- API response ổn định và dễ version
- frontend có thể tiêu thụ contract rõ ràng

## Phase 3 — Validation và error handling

### Việc cần làm
1. Validate `symbol`:
   - không rỗng
   - độ dài hợp lý
   - uppercase sau normalize
2. Validate `startDate`, `endDate`:
   - parse được theo `LocalDate`
   - `startDate <= endDate`
3. Thêm exception domain hoặc application-level:
   - `SymbolNotFoundException`
   - `InvalidDateRangeException`
   - `InvalidSymbolException`
4. Thêm global exception handler cho service.

### Error response nên chuẩn hóa
```json
{
  "error": "SYMBOL_NOT_FOUND",
  "message": "No market data found for symbol FPTX",
  "path": "/market/price/FPTX",
  "timestamp": "2026-06-05T09:45:00Z"
}
```

### Definition of done cho phase 3
- request sai không gây 500 không cần thiết
- 4xx/5xx được phân tách rõ ràng
- log dễ hiểu, frontend dễ xử lý

## Phase 4 — Quyết định vai trò RabbitMQ consumer

### Trạng thái hiện tại
`MarketDataConsumer` chỉ log raw message từ queue `market_service_price_q`.

### Hướng A — giữ listener ở mức log/freshness hook
Phù hợp nếu market-service chỉ là read layer từ DB.

Triển khai tối thiểu:
- parse message JSON
- log `symbols`, `source`, `timestamp`
- có thể lưu `lastUpdatedAt` trong cache/metric
- invalidate cache theo symbol nếu sau này có cache layer

### Hướng B — dùng listener cho cache invalidation
Nếu sau này thêm caching cho latest price hoặc OHLC:
- listener đọc `symbols[]`
- xóa cache key liên quan
- lần request sau query DB mới

### Không khuyến nghị trong giai đoạn hiện tại
- không dùng listener để upsert `stock_prices` / `financial_ratios`
- không coi RabbitMQ payload là full snapshot market data

### Definition of done cho phase 4
- vai trò listener được viết rõ trong docs và code
- không còn ambiguity giữa writer và reader

## Phase 5 — Tích hợp với frontend và gateway

### Frontend
1. Thêm `marketApi` vào `frontend/src/lib/api.ts`.
2. Tạo types riêng cho:
   - latest price
   - OHLC series
   - financial ratio list
3. Tích hợp vào:
   - `frontend/src/app/dashboard/page.tsx`
   - `frontend/src/components/charts/OHLCChart.tsx`
   - `frontend/src/app/dashboard/portfolio/page.tsx` nếu cần latest price để tính value

### Gateway
Nếu `api-gateway` là entry point bắt buộc:
- thêm route/proxy đến `market-service`
- đảm bảo auth được enforce qua gateway

### Definition of done cho phase 5
- frontend render dữ liệu market thật
- contract giữa frontend và market-service khớp nhau
- loading/error/empty state hoạt động đúng

## Phase 6 — Test coverage

### Unit tests nên có
- normalize symbol
- parse date range
- latest price có tính `change` và `changePercent` đúng
- getOhlc trả range đã sort đúng
- getRatios trả danh sách đúng thứ tự
- ném đúng exception khi không có data

### Integration tests nên có
- query được PostgreSQL thật hoặc testcontainer
- controller trả JSON đúng shape
- invalid request trả đúng status code

### Messaging tests nên có
- listener parse được payload `price.updated`
- listener không crash khi payload thiếu field optional

## Backlog kỹ thuật nên cân nhắc

### 1. Tách application service rõ hơn
Sau khi logic lớn dần, có thể tách:
- `LatestPriceQueryService`
- `OhlcQueryService`
- `FinancialRatioQueryService`

### 2. Thêm pagination hoặc limit cho ratio/history
Nếu sau này ratios nhiều hơn, có thể cần pagination hoặc `latestOnly=true`.

### 3. Bổ sung freshness metadata
Nếu frontend cần biết dữ liệu cũ hay mới:
- thêm field `asOfDate`
- hoặc thêm endpoint/status riêng cho market freshness

### 4. Đồng bộ naming với frontend
Nên thống nhất dứt điểm field names giữa backend DTO và frontend types thay vì để frontend tự đoán mapping.

## File dự kiến bị tác động khi implement code

### market-service
- `services/market-service/src/main/java/com/stockwise/market/application/service/MarketService.java`
- `services/market-service/src/main/java/com/stockwise/market/domain/repository/StockPriceRepository.java`
- `services/market-service/src/main/java/com/stockwise/market/domain/repository/FinancialRatioRepository.java`
- `services/market-service/src/main/java/com/stockwise/market/adapter/in/web/MarketController.java`
- package DTO / mapper / exception / handler mới
- có thể cả `messaging/MarketDataConsumer.java`

### frontend
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/app/dashboard/page.tsx`
- `frontend/src/components/charts/OHLCChart.tsx`

### gateway nếu đi qua gateway
- route/proxy config trong `services/api-gateway/`

## Thứ tự triển khai khuyến nghị

1. Query DB thật trong market-service
2. DTO hóa response
3. Validation + error handling
4. Test unit/integration
5. Xác định listener behavior
6. Tích hợp frontend
7. Tích hợp gateway nếu cần

## Kết luận

Bước nâng cấp market-service không nên bắt đầu từ UI. Nó nên bắt đầu bằng việc làm cho backend market trở thành nguồn đọc dữ liệu tin cậy từ PostgreSQL. Khi contract backend ổn định, frontend và gateway mới tích hợp sau để tránh đổi API nhiều lần.
