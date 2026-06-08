# Market Service — API Contract

## Mục tiêu của tài liệu này

Tài liệu này đề xuất contract cho `market-service` dựa trên:
- endpoint đang tồn tại trong source hiện tại
- schema dữ liệu trong PostgreSQL
- nhu cầu thực tế của frontend dashboard/chart
- các mismatch đang tồn tại giữa Java entity và TypeScript types

Mục tiêu là tránh trả trực tiếp JPA entity và thay vào đó dùng DTO ổn định, dễ version và dễ tích hợp frontend.

## Endpoint hiện có trong source

`MarketController` hiện expose:
- `GET /market/price/{symbol}`
- `GET /market/ratio/{symbol}`
- `GET /market/ohlc/{symbol}`

Về mặt routing, có thể giữ nguyên 3 endpoint này để giảm thay đổi. Phần cần cập nhật là shape response, validation và error handling.

## Vấn đề của contract hiện tại

### 1. Controller đang trả entity trực tiếp
Nếu trả trực tiếp `StockPrice` và `FinancialRatio`, API sẽ bị coupling chặt với persistence model.

### 2. Frontend type không khớp field name
Frontend hiện định nghĩa `StockPrice` như sau:
- `date`
- `open`
- `high`
- `low`
- `close`
- `volume`

Trong khi backend entity dùng `tradeDate`.

### 3. Latest price endpoint chưa phản ánh đúng nhu cầu UI
UI thường cần:
- latest close/price
- change
- changePercent
- updatedAt

Những field này không có sẵn ở entity nếu chỉ lấy một record duy nhất.

## Contract đề xuất

## 1. GET `/market/price/{symbol}`

### Mục đích
Trả dữ liệu giá mới nhất của một mã, đủ để hiển thị card overview hoặc giá tức thời.

### Auth
- Nên là `required` theo kiến trúc tổng thể của dự án.

### Request
- Path param: `symbol`
- Quy tắc: normalize uppercase và trim whitespace trước khi query

### Response 200

```json
{
  "symbol": "FPT",
  "price": 120000,
  "open": 118600,
  "high": 121000,
  "low": 118400,
  "close": 120000,
  "volume": 1543200,
  "change": 1400,
  "changePercent": 1.18,
  "tradeDate": "2026-06-05",
  "updatedAt": "2026-06-05T15:00:00Z"
}
```

### Cách tính đề xuất
- `price`: alias của `close`
- `change`: latest.close - previous.close
- `changePercent`: `(change / previous.close) * 100`
- `updatedAt`: có thể lấy từ `tradeDate` trong giai đoạn đầu, hoặc dùng timestamp freshness khi có tracking rõ hơn

### Response lỗi
- `400 INVALID_SYMBOL`
- `404 SYMBOL_NOT_FOUND`
- `503 MARKET_DATA_UNAVAILABLE`

### DTO đề xuất

```java
public record LatestPriceResponse(
    String symbol,
    BigDecimal price,
    BigDecimal open,
    BigDecimal high,
    BigDecimal low,
    BigDecimal close,
    Long volume,
    BigDecimal change,
    BigDecimal changePercent,
    LocalDate tradeDate,
    Instant updatedAt
) {}
```

## 2. GET `/market/ohlc/{symbol}`

### Mục đích
Trả series OHLC để hiển thị chart hoặc analytics đơn giản.

### Auth
- `required`

### Request
- Path param: `symbol`
- Query params:
  - `startDate=YYYY-MM-DD`
  - `endDate=YYYY-MM-DD`
- Trong giai đoạn đầu có thể giữ default value như controller hiện tại, nhưng về lâu dài nên yêu cầu explicit range hoặc có default rõ ràng như 30 ngày gần nhất.

### Response 200

```json
{
  "symbol": "FPT",
  "startDate": "2026-05-01",
  "endDate": "2026-06-05",
  "data": [
    {
      "date": "2026-06-03",
      "open": 118000,
      "high": 119500,
      "low": 117800,
      "close": 119000,
      "volume": 1210000
    },
    {
      "date": "2026-06-04",
      "open": 119000,
      "high": 120500,
      "low": 118700,
      "close": 118600,
      "volume": 980000
    },
    {
      "date": "2026-06-05",
      "open": 118600,
      "high": 121000,
      "low": 118400,
      "close": 120000,
      "volume": 1543200
    }
  ]
}
```

### DTO đề xuất

```java
public record OhlcPointResponse(
    LocalDate date,
    BigDecimal open,
    BigDecimal high,
    BigDecimal low,
    BigDecimal close,
    Long volume
) {}

public record OhlcSeriesResponse(
    String symbol,
    LocalDate startDate,
    LocalDate endDate,
    List<OhlcPointResponse> data
) {}
```

### Response lỗi
- `400 INVALID_DATE_RANGE`
- `400 INVALID_SYMBOL`
- `404 SYMBOL_NOT_FOUND`

### Quy tắc xử lý
- `startDate <= endDate`
- query xong sort tăng dần theo ngày để frontend render chart dễ hơn
- nếu không có data trong range thì trả `404` hoặc `200` với `data: []`; nên thống nhất một hướng cho toàn team. Khuyến nghị: `200` với `data: []` cho chart dễ xử lý hơn.

## 3. GET `/market/ratio/{symbol}`

### Mục đích
Trả danh sách financial ratios cho symbol theo period.

### Auth
- `required`

### Response 200

```json
{
  "symbol": "FPT",
  "ratios": [
    {
      "period": "Q4 2025",
      "peRatio": 25.5,
      "pbRatio": 3.2,
      "eps": 4.05,
      "roe": 0.18,
      "roa": 0.09
    }
  ]
}
```

### DTO đề xuất

```java
public record FinancialRatioResponse(
    String period,
    BigDecimal peRatio,
    BigDecimal pbRatio,
    BigDecimal eps,
    BigDecimal roe,
    BigDecimal roa
) {}

public record FinancialRatioListResponse(
    String symbol,
    List<FinancialRatioResponse> ratios
) {}
```

### Response lỗi
- `400 INVALID_SYMBOL`
- `404 SYMBOL_NOT_FOUND`

## Error format đề xuất

Nên thống nhất error envelope dùng chung cho service Java:

```json
{
  "error": "SYMBOL_NOT_FOUND",
  "message": "No market data found for symbol FPTX",
  "path": "/market/price/FPTX",
  "timestamp": "2026-06-05T09:45:00Z"
}
```

### Gợi ý code error
- `INVALID_SYMBOL`
- `INVALID_DATE_RANGE`
- `SYMBOL_NOT_FOUND`
- `MARKET_DATA_UNAVAILABLE`
- `INTERNAL_SERVER_ERROR`

## Mapping giữa DB / Entity / DTO / Frontend

### Stock price mapping

| Layer | Field |
|---|---|
| PostgreSQL | `trade_date` |
| JPA entity | `tradeDate` |
| OHLC API response | `date` |
| Latest price response | `tradeDate` |
| Frontend current type | `date` |

Khuyến nghị:
- với latest price response có thể dùng `tradeDate`
- với chart series nên dùng `date` để frontend trực quan hơn
- frontend nên có type riêng cho latest price, không reuse `OHLCV` cho mọi trường hợp

## Frontend type đề xuất

Hiện tại `frontend/src/lib/types.ts` chỉ có một `StockPrice` đơn giản. Nên tách ra như sau:

```ts
export interface LatestPrice {
  symbol: string;
  price: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change: number;
  changePercent: number;
  tradeDate: string;
  updatedAt: string;
}

export interface OhlcPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OhlcSeries {
  symbol: string;
  startDate: string;
  endDate: string;
  data: OhlcPoint[];
}

export interface FinancialRatioItem {
  period: string;
  peRatio: number | null;
  pbRatio: number | null;
  eps: number | null;
  roe: number | null;
  roa: number | null;
}
```

## Query implementation gợi ý

### Latest price
- lấy 2 record mới nhất theo `tradeDate DESC`
- record đầu để trả latest
- record thứ hai để tính `change` và `changePercent`

### OHLC range
- `findBySymbolAndTradeDateBetween(symbol, start, end)`
- sort tăng dần theo `tradeDate`

### Ratios
- `findBySymbol(symbol)`
- có thể cần thêm sort theo `period DESC` hoặc trường thời gian rõ ràng hơn sau này

## Response compatibility strategy

Trong ít nhất một sprint đầu khi frontend mới tích hợp:
- giữ path endpoint như cũ
- thay response sang DTO mới
- cập nhật frontend client/types trong cùng PR hoặc PR song hành

## Kết luận

Contract hiện tại của `market-service` mới đúng ở mức routing. Muốn service sẵn sàng cho frontend và các consumer khác, cần:
- tách DTO khỏi entity
- thống nhất error format
- chuẩn hóa date/symbol handling
- mở rộng latest-price response để phục vụ UI thực tế
