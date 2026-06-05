# Market Service — Testing and Operations

## Mục tiêu

Tài liệu này mô tả cách chạy `market-service`, cách kiểm tra phụ thuộc của nó, và cách smoke test những API market hiện có.

Vì `market-service` phụ thuộc vào PostgreSQL và RabbitMQ, việc test nên được hiểu ở 3 mức:
- test compile/package ở cấp service
- smoke test runtime ở local hoặc Docker Compose
- integration test với dữ liệu thật đã được ingest bởi `data-pipeline`

## Thành phần phụ thuộc

`market-service` hiện phụ thuộc vào:
- PostgreSQL: bảng `stock_prices`, `financial_ratios`
- RabbitMQ: queue `market_service_price_q`, exchange `market.exchange`
- optional: `api-gateway` nếu muốn request đi qua entry point chung

### Port và container hiện tại

Từ `docker-compose.yml`:
- `market-service`: host `18082` → container `8082`
- `postgres`: host `15432` → container `5432`
- `rabbitmq`: host `5672`
- `api-gateway`: host `18080`

## Chạy service bằng Docker Compose

### Chạy riêng hạ tầng và market-service

```bash
docker compose up --build postgres rabbitmq market-service
```

### Chạy full stack

```bash
docker compose up --build
```

### Kiểm tra service có lên không
- `market-service`: [http://localhost:18082/actuator/health](http://localhost:18082/actuator/health)
- RabbitMQ management: [http://localhost:15672](http://localhost:15672)

Nếu mọi thứ ổn, `actuator/health` nên trả trạng thái `UP`.

## Chạy service bằng Maven local

```bash
cd services/market-service
mvn test
mvn package
mvn spring-boot:run
```

Khi chạy local ngoài Docker, cần chắc chắn các biến môi trường DB/RabbitMQ đúng với máy hiện tại. Theo `application.yml`, mặc định service sẽ tìm:
- PostgreSQL tại `localhost:5432`
- RabbitMQ tại `localhost:5672`

Nếu bạn đang dùng Docker Compose, Postgres thực tế map ra host `15432`, nên cần truyền env phù hợp khi chạy local:

```bash
set POSTGRES_HOST=localhost
set POSTGRES_PORT=15432
set POSTGRES_DB=stockwise
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres
set RABBITMQ_HOST=localhost
set RABBITMQ_PORT=5672
set RABBITMQ_USER=guest
set RABBITMQ_PASS=guest
mvn spring-boot:run
```

## Smoke test REST API

Lưu ý: với source hiện tại, endpoint vẫn trả mock data. Sau khi implement DB query thật, các lệnh này vẫn là bộ smoke test tốt.

### 1. Latest price

```bash
curl "http://localhost:18082/market/price/FPT"
```

Kỳ vọng hiện tại:
- trả JSON có `symbol`, `tradeDate`, `open`, `high`, `low`, `close`, `volume`
- nhưng là mock/hardcoded

### 2. Ratio

```bash
curl "http://localhost:18082/market/ratio/FPT"
```

Kỳ vọng hiện tại:
- trả một phần tử ratio hardcoded

### 3. OHLC range

```bash
curl "http://localhost:18082/market/ohlc/FPT?startDate=2026-05-01&endDate=2026-06-05"
```

Kỳ vọng hiện tại:
- trả danh sách 1 phần tử mock
- sau khi implement đầy đủ, nên trả cả series theo khoảng ngày

## Kiểm tra dữ liệu PostgreSQL trước khi test API

Vì market-service nên đọc từ DB, cần xác nhận DB có data thật.

### Kiểm tra bảng `stock_prices`

```sql
SELECT symbol, trade_date, open, high, low, close, volume
FROM stock_prices
WHERE symbol = 'FPT'
ORDER BY trade_date DESC
LIMIT 5;
```

### Kiểm tra bảng `financial_ratios`

```sql
SELECT symbol, period, pe_ratio, pb_ratio, eps, roe, roa
FROM financial_ratios
WHERE symbol = 'FPT'
ORDER BY period DESC;
```

Nếu hai query này không có dữ liệu, API market sau khi chuyển sang DB query sẽ không trả được dữ liệu thật.

## Kiểm tra luồng data-pipeline → PostgreSQL

Để market-service có dữ liệu thật, `data-pipeline` phải ingest trước.

### Cách kiểm tra thực tế
1. Đảm bảo `tracked_symbols` có symbol cần test.
2. Chạy `data-pipeline` hoặc trigger stream A.
3. Kiểm tra DB có record mới trong `stock_prices` và `financial_ratios`.
4. Kiểm tra RabbitMQ có event `price.updated`.

Từ source hiện tại, Stream A:
- fetch giá qua `VnStockFetcher`
- fetch ratio qua `YahooFinanceFetcher`
- upsert DB qua `PriceRepository`
- publish `market.exchange / price.updated`

## Kiểm tra RabbitMQ listener

Hiện tại `MarketDataConsumer` chỉ log message. Smoke test listener ở giai đoạn này là xác nhận:
- queue `market_service_price_q` đã bind đúng
- khi `data-pipeline` publish event thì market-service nhận được log

### Dấu hiệu đúng
- RabbitMQ management UI có queue `market_service_price_q`
- khi stream A chạy, log của market-service có dòng kiểu:

```text
Received price update from RabbitMQ: {...}
```

## Test cases nên có khi triển khai đầy đủ

## 1. Unit tests cho service

### Latest price
- có 2 record liên tiếp → tính `change` và `changePercent` đúng
- có 1 record duy nhất → `change` và `changePercent` theo quy ước đã chọn
- không có record → ném `SymbolNotFoundException`

### OHLC
- query range đúng khoảng ngày
- dữ liệu trả về đã sort theo `tradeDate ASC`
- `startDate > endDate` → `INVALID_DATE_RANGE`

### Ratios
- trả danh sách ratio của symbol đúng
- không có ratio → `SYMBOL_NOT_FOUND` hoặc empty list theo contract

## 2. Controller tests
- `GET /market/price/{symbol}` trả status 200 với JSON đúng shape
- input symbol rỗng hoặc invalid trả 400
- symbol không tồn tại trả 404
- lỗi nội bộ trả 500 với error envelope chuẩn

## 3. Repository tests
- `findTopBySymbolOrderByTradeDateDesc` trả đúng latest row
- `findBySymbolAndTradeDateBetween...` lọc đúng range
- `findBySymbolOrderByPeriodDesc` trả đúng thứ tự mong muốn

## 4. Messaging tests
- listener không crash khi message hợp lệ
- listener log hoặc invalidate cache khi có `symbols[]`
- listener xử lý tốt khi payload thiếu field không quan trọng

## Checklist vận hành trước khi merge PR market-service

### Backend
```bash
cd services/market-service
mvn test
mvn package
```

### Docker
```bash
docker compose config
docker compose up --build market-service
```

### Runtime validation
- `actuator/health` trả `UP`
- `GET /market/price/{symbol}` có response đúng
- `GET /market/ratio/{symbol}` có response đúng
- `GET /market/ohlc/{symbol}` có response đúng
- log RabbitMQ consumer không có exception bất thường

### Data validation
- DB có dữ liệu thật cho symbol test
- symbol được normalize uppercase
- nếu frontend đã tích hợp thì chart không crash khi `data: []`

## Các điểm dễ gây lỗi khi chạy local

### 1. Sai port PostgreSQL
`application.yml` mặc định dùng `5432`, nhưng Docker Compose map ra host `15432`. Nếu chạy market-service local ngoài Docker mà quên override env, service sẽ không kết nối được DB.

### 2. DB không có dữ liệu market
Ngay cả khi service chạy ổn, API vẫn không trả dữ liệu thật nếu `data-pipeline` chưa ingest gì.

### 3. RabbitMQ queue chưa bind đúng
Nếu queue `market_service_price_q` không tồn tại hoặc binding không đúng, listener sẽ không nhận được event `price.updated`.

### 4. Frontend kỳ vọng field name khác backend
Nếu frontend tích hợp sớm khi backend còn trả entity trực tiếp, mismatch `date` vs `tradeDate` sẽ gây lỗi mapping.

## Khuyến nghị test symbol mẫu
Nên dùng các mã đã được track hoặc seed sẵn trong hệ thống, ví dụ:
- `FPT`
- `VCB`
- `HPG`

Miễn là kiểm tra được chúng thực sự có record trong DB trước khi test API.

## Kết luận

Vận hành `market-service` đúng cách phụ thuộc nhiều vào việc nhìn nó như một phần của luồng dữ liệu lớn hơn:
- `data-pipeline` phải ingest thành công
- PostgreSQL phải có record thật
- RabbitMQ phải hoạt động
- `market-service` chỉ phát huy vai trò khi query được dữ liệu đã chuẩn hóa

Vì vậy test market-service không nên dừng ở `mvn package`, mà cần có ít nhất một vòng smoke test với DB và dữ liệu thật.
