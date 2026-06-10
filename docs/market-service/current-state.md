# Market Service — Current State

## Tổng quan

`market-service` là Spring Boot microservice được khai báo trong `docker-compose.yml` và expose port `18082` (host) / `8082` (container).

Về cấu trúc thư mục:

```
services/market-service/
├── pom.xml
├── Dockerfile
└── src/main/
    ├── java/com/stockwise/market/
    │   ├── MarketServiceApplication.java
    │   ├── adapter/in/web/
    │   │   └── MarketController.java
    │   ├── application/
    │   │   ├── service/MarketService.java
    │   │   └── port/in/
    │   │       ├── GetStockPriceUseCase.java
    │   │       └── GetFinancialRatioUseCase.java
    │   ├── domain/
    │   │   ├── entity/
    │   │   │   ├── StockPrice.java
    │   │   │   └── FinancialRatio.java
    │   │   └── repository/
    │   │       ├── StockPriceRepository.java
    │   │       └── FinancialRatioRepository.java
    │   ├── messaging/
    │   │   └── MarketDataConsumer.java
    │   └── config/
    │       └── RabbitConfig.java
    └── resources/
        └── application.yml
```

## Cấu hình runtime

File: [`services/market-service/src/main/resources/application.yml`](../../services/market-service/src/main/resources/application.yml)

```yaml
server:
  port: 8082

spring:
  datasource:
    url: jdbc:postgresql://${POSTGRES_HOST:localhost}:${POSTGRES_PORT:5432}/${POSTGRES_DB:stockwise}
    username: ${POSTGRES_USER:postgres}
    password: ${POSTGRES_PASSWORD:postgres}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: update
  rabbitmq:
    host: ${RABBITMQ_HOST:localhost}
    port: ${RABBITMQ_PORT:5672}
```

Điểm đáng lưu ý: `ddl-auto: update` nghĩa là JPA sẽ tự tạo schema. Tuy nhiên toàn bộ schema đã được init sẵn qua `infra/postgres/init.sql`, nên không cần JPA tạo bảng. Các bảng `stock_prices` và `financial_ratios` đã tồn tại với schema đầy đủ.

## Entity và Repository

### StockPrice

File: [`services/market-service/src/main/java/com/stockwise/market/domain/entity/StockPrice.java`](../../services/market-service/src/main/java/com/stockwise/market/domain/entity/StockPrice.java)

```java
@Entity
@Table(name = "stock_prices")
@Data
public class StockPrice {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String symbol;
    private LocalDate tradeDate;
    private BigDecimal open;
    private BigDecimal high;
    private BigDecimal low;
    private BigDecimal close;
    private Long volume;
}
```

Entity này mapping trực tiếp vào bảng `stock_prices` trong PostgreSQL. Tên cột trong DB là `trade_date`, `open`, `high`, `low`, `close`, `volume`. Lombok `@Data` generate getter/setter.

### FinancialRatio

File: [`services/market-service/src/main/java/com/stockwise/market/domain/entity/FinancialRatio.java`](../../services/market-service/src/main/java/com/stockwise/market/domain/entity/FinancialRatio.java)

```java
@Entity
@Table(name = "financial_ratios")
@Data
public class FinancialRatio {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String symbol;
    private String period;
    private BigDecimal peRatio;
    private BigDecimal pbRatio;
    private BigDecimal eps;
    private BigDecimal roe;
    private BigDecimal roa;
}
```

Entity này mapping vào bảng `financial_ratios`. Tên cột DB là `pe_ratio`, `pb_ratio`, `eps`, `roe`, `roa` — JPA tự động convert camelCase Java field sang snake_case SQL column.

### Repository

File: [`services/market-service/src/main/java/com/stockwise/market/domain/repository/StockPriceRepository.java`](../../services/market-service/src/main/java/com/stockwise/market/domain/repository/StockPriceRepository.java)

```java
public interface StockPriceRepository extends JpaRepository<StockPrice, Long> {
    List<StockPrice> findBySymbolAndTradeDateBetween(String symbol, LocalDate start, LocalDate end);
}
```

File: [`services/market-service/src/main/java/com/stockwise/market/domain/repository/FinancialRatioRepository.java`](../../services/market-service/src/main/java/com/stockwise/market/domain/repository/FinancialRatioRepository.java)

```java
public interface FinancialRatioRepository extends JpaRepository<FinancialRatio, Long> {
    List<FinancialRatio> findBySymbol(String symbol);
}
```

Cả hai repository đều tồn tại đúng nhưng **chưa được inject vào `MarketService`** để sử dụng. Đây là phần cần implement trong bước nâng cấp.

## Controller

File: [`services/market-service/src/main/java/com/stockwise/market/adapter/in/web/MarketController.java`](../../services/market-service/src/main/java/com/stockwise/market/adapter/in/web/MarketController.java)

```java
@RestController
@RequestMapping("/market")
@RequiredArgsConstructor
public class MarketController {
    private final GetStockPriceUseCase getStockPriceUseCase;
    private final GetFinancialRatioUseCase getFinancialRatioUseCase;

    @GetMapping("/price/{symbol}")
    public ResponseEntity<StockPrice> getPrice(@PathVariable String symbol) {
        return ResponseEntity.ok(getStockPriceUseCase.getLatestPrice(symbol));
    }

    @GetMapping("/ratio/{symbol}")
    public ResponseEntity<List<FinancialRatio>> getRatio(@PathVariable String symbol) {
        return ResponseEntity.ok(getFinancialRatioUseCase.getRatios(symbol));
    }

    @GetMapping("/ohlc/{symbol}")
    public ResponseEntity<List<StockPrice>> getOhlc(
            @PathVariable String symbol,
            @RequestParam(defaultValue = "2024-01-01") String startDate,
            @RequestParam(defaultValue = "2025-12-31") String endDate) {
        return ResponseEntity.ok(getStockPriceUseCase.getOhlc(symbol, startDate, endDate));
    }
}
```

Controller đã đúng cấu trúc hexagonal. Tuy nhiên:
- endpoint trả trực tiếp entity, không qua DTO
- không có validation symbol uppercase
- không có error handling cho trường hợp không tìm thấy symbol
- không có auth — mặc dù kế hoạch nói auth required, hiện tại endpoint không có annotation `@PreAuthorize`

## Business logic (phần stub)

File: [`services/market-service/src/main/java/com/stockwise/market/application/service/MarketService.java`](../../services/market-service/src/main/java/com/stockwise/market/application/service/MarketService.java)

Đây là phần cần thay đổi lớn nhất. Toàn bộ logic hiện tại là hardcode:

```java
@Service
public class MarketService implements GetStockPriceUseCase, GetFinancialRatioUseCase {
    @Override
    public StockPrice getLatestPrice(String symbol) {
        StockPrice price = new StockPrice();
        price.setId(1L);
        price.setSymbol(symbol);
        price.setTradeDate(LocalDate.now());
        price.setOpen(new BigDecimal("100.00"));
        price.setHigh(new BigDecimal("105.00"));
        price.setLow(new BigDecimal("99.00"));
        price.setClose(new BigDecimal("103.50"));
        price.setVolume(1000000L);
        return price;
    }

    @Override
    public List<StockPrice> getOhlc(String symbol, String startDate, String endDate) {
        return List.of(getLatestPrice(symbol)); // chỉ trả 1 record
    }

    @Override
    public List<FinancialRatio> getRatios(String symbol) {
        FinancialRatio ratio = new FinancialRatio();
        ratio.setId(1L);
        ratio.setSymbol(symbol);
        ratio.setPeriod("Q4 2025");
        ratio.setPeRatio(new BigDecimal("25.50"));
        ratio.setPbRatio(new BigDecimal("3.20"));
        ratio.setEps(new BigDecimal("4.05"));
        ratio.setRoe(new BigDecimal("0.18"));
        ratio.setRoa(new BigDecimal("0.09"));
        return List.of(ratio);
    }
}
```

`getOhlc` hiện chỉ trả một record (copy của `getLatestPrice`). Cần implement truy vấn theo date range thực sự.

## RabbitMQ Consumer

File: [`services/market-service/src/main/java/com/stockwise/market/messaging/MarketDataConsumer.java`](../../services/market-service/src/main/java/com/stockwise/market/messaging/MarketDataConsumer.java)

```java
@RabbitListener(queues = "market_service_price_q")
public void consumePriceUpdate(String message) {
    log.info("Received price update from RabbitMQ: {}", message);
}
```

Consumer hiện tại chỉ nhận message rồi log. Không có logic gì khác. Phần này cần quyết định rõ vai trò của nó trong hệ thống:
- nếu chỉ dùng để log/notify thì giữ nguyên
- nếu cần dùng để invalidate cache hay refresh read model thì cần implement thêm

### RabbitMQ Config

File: [`services/market-service/src/main/java/com/stockwise/market/config/RabbitConfig.java`](../../services/market-service/src/main/java/com/stockwise/market/config/RabbitConfig.java)

```java
@Configuration
public class RabbitConfig {
    public static final String MARKET_EXCHANGE = "market.exchange";
    public static final String MARKET_PRICE_QUEUE = "market_service_price_q";
    public static final String MARKET_PRICE_ROUTING_KEY = "price.updated";

    @Bean public TopicExchange marketExchange() { ... }
    @Bean public Queue marketPriceQueue() { ... }
    @Bean public Binding marketPriceBinding(...) { ... }
}
```

Queue, exchange và binding đã khai báo đầy đủ qua Spring AMQP. Điểm đáng lưu ý là queue name trùng khớp với payload contract mà `data-pipeline` gửi: exchange `market.exchange`, routing key `price.updated`.

## Maven và Docker

File: [`services/market-service/pom.xml`](../../services/market-service/pom.xml)

Dependencies chính:
- `spring-boot-starter-web` (REST)
- `spring-boot-starter-data-jpa` (PostgreSQL ORM)
- `spring-boot-starter-security` (đã include nhưng chưa dùng)
- `spring-boot-starter-amqp` (RabbitMQ)
- `postgresql` driver
- `lombok`, `spring-boot-starter-validation`, `actuator`

Dockerfile dùng multi-stage build:
- build stage: `maven:3.9.6-eclipse-temurin-21-alpine`
- run stage: `eclipse-temurin:21-jre-alpine`
- expose port 8082

## Maven test command

```bash
cd services/market-service
mvn test
mvn package
```

## Các phần đang stub hoặc thiếu

| Phần | Trạng thái | Ghi chú |
|---|---|---|
| Controller endpoints | có rồi | trả entity thay vì DTO, chưa có auth |
| Entity StockPrice/FinancialRatio | có rồi | đúng cấu trúc, map đúng bảng DB |
| Repository interface | có rồi | chưa được inject vào service |
| Business logic (service) | stub | hardcode mock data, không truy vấn DB |
| RabbitMQ consumer | stub | chỉ log, chưa có business logic |
| RabbitMQ config | hoàn thiện | queue/exchange/binding đúng |
| Validation symbol | thiếu | không chuẩn hóa uppercase, không validate |
| Error handling | thiếu | không có 404/503 response khi không có data |
| DTO layer | thiếu | trả entity trực tiếp |
| Auth integration | thiếu | spring-security đã include nhưng chưa bật |
| Unit test | chưa thấy | cần tạo |
