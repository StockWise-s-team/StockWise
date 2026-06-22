# Portfolio Service — Complete UML

> All diagrams are derived directly from the code under `services/portfolio-service`
> (Spring Boot 3.2.5, Java 21, **hexagonal / ports & adapters**).
> Large views are split into cohesive sub-diagrams so nothing is ambiguous.
>
> **Mermaid note:** class diagrams use `~T~` for generics (e.g. `List~Order~`);
> sequence messages use `List[Order]` — both avoid the `<...>` HTML pitfall.

## Contents
1. [Use-Case diagram](#1-use-case-diagram)
2. [Layered / Package diagram](#2-layered--package-diagram)
3. [Component diagram (runtime wiring)](#3-component-diagram-runtime-wiring)
4. [Class diagrams](#4-class-diagrams) — split by concern
   - 4.1 [Domain entities](#41-domain-entities)
   - 4.2 [Persistence repositories](#42-persistence-repositories)
   - 4.3 [Web inbound adapter + inbound ports](#43-web-inbound-adapter--inbound-ports)
   - 4.4 [Application services](#44-application-services)
   - 4.5 [Validation subsystem](#45-validation-subsystem)
   - 4.6 [Reservation subsystem](#46-reservation-subsystem)
   - 4.7 [Matching subsystem](#47-matching-subsystem)
   - 4.8 [Outbound ports + messaging adapters](#48-outbound-ports--messaging-adapters)
   - 4.9 [Security](#49-security)
   - 4.10 [Error handling](#410-error-handling)
5. [State machine — Order lifecycle](#5-state-machine--order-lifecycle)
6. [Sequence diagrams](#6-sequence-diagrams)
7. [Activity diagrams](#7-activity-diagrams)
8. [Deployment diagram](#8-deployment-diagram)

---

## 1. Use-Case diagram

```mermaid
flowchart LR
    trader([Trader]):::actor
    mkt([Market Service]):::actor
    ai([AI Service]):::actor

    subgraph SYS["Portfolio Service"]
        uc1(["View portfolio"])
        uc2(["View order history"])
        uc3(["View realized PnL"])
        uc4(["Place order"])
        uc5(["Cancel order"])
        uc6(["Match pending orders"])
        uc7(["Publish portfolio events"])
    end

    trader -->|requests| uc1
    trader -->|requests| uc2
    trader -->|requests| uc3
    trader -->|commands| uc4
    trader -->|commands| uc5
    mkt -->|price change| uc6
    uc4 -. produces .-> uc7
    uc5 -. produces .-> uc7
    uc6 -. produces .-> uc7
    uc7 -->|notifies| ai

    classDef actor fill:#e8e8e8,stroke:#333,stroke-width:1px;
```

All trader use-cases require a valid JWT (resolved from the gateway-forwarded
`Authorization: Bearer` header). `uc6` is system-triggered by a RabbitMQ message.

---

## 2. Layered / Package diagram

Each node is **one package**; details live in the table below. Solid arrow =
compile-time dependency; dotted arrow = realization / runtime wiring.
Dependency rule: arrows point **inward** — `domain.entity` depends on nothing.

```mermaid
flowchart TB
    subgraph IN["adapter.in — driving"]
        WEB["Web Adapter"]
        SEC["Security Adapter"]
        MIN["Message Listener"]
    end
    subgraph APP["application"]
        PIN["Inbound Ports"]
        SVC["Portfolio Services"]
        ORD["Order Services"]
        POUT["Outbound Ports"]
        EXC["Application Errors"]
    end
    subgraph DOM["domain"]
        ENT["Domain Entities"]
        REPO["Repositories"]
    end
    subgraph OUT["adapter.out — driven"]
        MOUT["Message Publishers"]
    end
    subgraph INFRA["config + runtime"]
        CFG["Configuration"]
        JPA["Persistence Runtime"]
    end

    WEB -->|drives| PIN
    WEB -->|handles| EXC
    WEB -->|presents| ENT
    MIN -->|triggers| ORD
    PIN -->|speaks domain| ENT
    POUT -->|emits domain state| ENT
    SVC -. realizes .-> PIN
    ORD -. realizes .-> PIN
    SVC -->|uses| POUT
    SVC -->|persists through| REPO
    SVC -->|works with| ENT
    SVC -->|delegates to| ORD
    ORD -->|uses| POUT
    ORD -->|persists through| REPO
    ORD -->|changes| ENT
    ORD -->|signals| EXC
    REPO -->|stores| ENT
    MOUT -. adapts .-> POUT
    MOUT -->|publishes| ENT
    REPO -. backed by .-> JPA
    CFG -->|configures| SEC
    SEC -. protects .-> WEB
```

| Package | Key contents |
| --- | --- |
| `adapter.in.web` | `PortfolioController`, `dto/*` (PlaceOrderRequest, OrderResponse, OrderHistoryResponse, PortfolioResponse, PnlResponse, ErrorResponse), `OrderResponseMapper`, `UserIdResolver`, `RestExceptionHandler` |
| `adapter.in.security` | `JwtAuthenticationFilter`, `JwtTokenProvider`, `JwtTokenProviderImpl` |
| `adapter.in.messaging` | `PriceUpdateListener` |
| `application.port.in` | `PlaceOrderUseCase`, `CancelOrderUseCase`, `GetPortfolioUseCase`, `GetPnLUseCase` |
| `application.service` | `PortfolioService`, `PortfolioAccountService` |
| `application.service.order` | `OrderConstants`, `ValidatedOrderRequest`; `lifecycle/` (PlaceOrderService, CancelOrderService, OrderFactory); `validation/`; `reservation/`; `match/` (incl. OrderMatchProcessor) |
| `application.port.out` | `OrderEventPublisher`, `PortfolioEventPublisher` |
| `application.exception` | `BadRequestException`, `ConflictException`, `NotFoundException` |
| `domain.entity` | `Portfolio`, `Holding`, `Order`, `Transaction` |
| `domain.repository` | `PortfolioRepository`, `HoldingRepository`, `OrderRepository`, `TransactionRepository` |
| `adapter.out.messaging` | `RabbitOrderEventPublisher`, `RabbitPortfolioEventPublisher` |
| `config` | `AppConfig`, `RabbitConfig`, `SecurityConfig` |

---

## 3. Component diagram (runtime wiring)

```mermaid
flowchart TB
    subgraph EXT["External systems"]
        FE["Client Gateway"]
        MKT["Market System"]
        AI["AI Consumer"]
        MQ(["Message Broker"])
        DB[("Portfolio Database")]
    end

    subgraph INA["Inbound adapters — adapter.in"]
        SEC["Authentication Boundary"]
        CTRL["REST API Adapter"]
        LST["Price Event Adapter"]
    end

    subgraph CORE["Application core"]
        subgraph PI["Inbound ports — port.in"]
            UC1["Order Command Port"]
            UC2["Cancel Command Port"]
            UC3["Portfolio Query Port"]
            UC4["PnL Query Port"]
        end
        POS["Order Placement"]
        COS["Order Cancellation"]
        PS["Portfolio Queries"]
        PAS["Account Access"]
        OMP["Order Matching"]
        OF["Order Creation"]
        VAL["Validation Policy"]
        RES["Reservation Policy"]
        MAT["Matching Policy"]
        subgraph PO["Outbound ports — port.out"]
            OEP["Order Events"]
            PEP["Portfolio Events"]
            REPO["Persistence Port"]
        end
    end

    subgraph OUTA["Outbound adapters — adapter.out"]
        ROEP["Order Event Adapter"]
        RPEP["Portfolio Event Adapter"]
        JPA["Persistence Adapter"]
    end

    FE -->|user request| SEC
    SEC -->|authorized request| CTRL
    CTRL -->|order command| UC1
    CTRL -->|cancel command| UC2
    CTRL -->|portfolio query| UC3
    CTRL -->|PnL query| UC4
    UC1 -. implemented by .-> POS
    UC2 -. implemented by .-> COS
    UC3 -. implemented by .-> PS
    UC4 -. implemented by .-> PS

    POS -->|checks policy| VAL
    POS -->|uses account| PAS
    POS -->|reserves assets| RES
    POS -->|creates order| OF
    POS -->|emits event| OEP
    POS -->|stores state| REPO
    COS -->|releases assets| RES
    COS -->|emits event| OEP
    COS -->|updates state| REPO
    PS -->|uses account| PAS
    PS -->|reads state| REPO
    PAS -->|persists account| REPO

    MKT -->|market event| MQ
    MQ -->|delivers event| LST
    LST -->|updates price context| VAL
    LST -->|starts matching| OMP
    OMP -->|applies policy| MAT
    OMP -->|emits event| PEP
    OMP -->|updates state| REPO

    OEP -. implemented by .-> ROEP
    PEP -. implemented by .-> RPEP
    REPO -. implemented by .-> JPA
    ROEP -->|order event| MQ
    RPEP -->|portfolio event| MQ
    MQ -->|portfolio update| AI
    JPA -->|stores state| DB
```

`PriceUpdateListener` writes the latest price into the shared `SymbolPriceCache`
(used by validation) **and** triggers `OrderMatchProcessor`.

---

## 4. Class diagrams

> Ports referenced across several views (`*Repository`, `*EventPublisher`,
> `OrderValidator`, `*StrategyRegistry`) are shown in full in their own subsection;
> elsewhere they appear as plain boxes to keep each view focused.

### 4.1 Domain entities

```mermaid
classDiagram
    class Portfolio {
        +UUID id
        +UUID userId
        +BigDecimal virtualCash
    }
    class Holding {
        +UUID id
        +UUID portfolioId
        +String symbol
        +Integer quantity
        +BigDecimal avgPrice
    }
    class Order {
        +UUID id
        +UUID userId
        +UUID portfolioId
        +String symbol
        +String type
        +BigDecimal price
        +Integer quantity
        +String status
        +LocalDateTime createdAt
        +LocalDateTime cancelledAt
        +prePersist() void
    }
    class Transaction {
        +UUID id
        +UUID portfolioId
        +String symbol
        +String type
        +BigDecimal price
        +Integer quantity
        +LocalDateTime executedAt
    }
    Portfolio "1" --> "0..*" Holding : contains
    Portfolio "1" --> "0..*" Order : tracks
    Portfolio "1" --> "0..*" Transaction : records
    note for Order "type in {BUY, SELL}; status in {PENDING, FILLED, CANCELLED}<br/>@PrePersist defaults status=PENDING, createdAt=now"
    note for Portfolio "userId references user-service; associations are by UUID (no JPA FK)"
```

### 4.2 Persistence repositories

```mermaid
classDiagram
    class JpaRepository {
        <<interface>>
        +save(entity) entity
        +findById(id) Optional
        +findAll() List
    }
    class PortfolioRepository {
        <<interface>>
        +findByUserId(UUID) Optional~Portfolio~
    }
    class HoldingRepository {
        <<interface>>
        +findByPortfolioId(UUID) List~Holding~
        +findByPortfolioIdAndSymbol(UUID, String) Optional~Holding~
    }
    class OrderRepository {
        <<interface>>
        +findByIdAndUserId(UUID, UUID) Optional~Order~
        +findByUserIdOrderByCreatedAtDesc(UUID) List~Order~
        +findBySymbolAndStatus(String, String) List~Order~
        +findLatestPriceBySymbol(String) BigDecimal
    }
    class TransactionRepository {
        <<interface>>
        +save(Transaction) Transaction
        +findByPortfolioIdOrderByExecutedAtDesc(UUID) List~Transaction~
    }
    JpaRepository <|-- PortfolioRepository : portfolio storage
    JpaRepository <|-- HoldingRepository : holding storage
    JpaRepository <|-- OrderRepository : order storage
    note for JpaRepository "Spring Data JpaRepository[Entity, UUID]"
    note for OrderRepository "findLatestPriceBySymbol = native query on stock_prices (data-pipeline table)"
    note for TransactionRepository "extends Spring Data Repository (write + one finder only)"
```

### 4.3 Web inbound adapter + inbound ports

```mermaid
classDiagram
    class PortfolioController {
        <<RestController>>
        +getPortfolio() ResponseEntity
        +placeOrder(PlaceOrderRequest) ResponseEntity
        +getOrders() ResponseEntity
        +cancelOrder(String) ResponseEntity
        +getPnl() ResponseEntity
    }
    class UserIdResolver {
        +resolveCurrentUserId() UUID
    }
    class OrderResponseMapper {
        +placed(Order) OrderResponse
        +cancelled(Order) OrderResponse
    }
    class PlaceOrderUseCase {
        <<interface>>
        +placeOrder(UUID, String, String, Integer) Order
        +placeOrder(UUID, String, String, Integer, BigDecimal) Order
    }
    class CancelOrderUseCase {
        <<interface>>
        +cancelOrder(UUID, Optional) Order
    }
    class GetPortfolioUseCase {
        <<interface>>
        +getPortfolio(UUID) Portfolio
        +getHoldings(UUID) List~Holding~
        +getTransactionHistory(UUID) List~Transaction~
        +getOrderHistory(UUID) List~Order~
    }
    class GetPnLUseCase {
        <<interface>>
        +getTotalPnl(UUID) BigDecimal
    }
    class PlaceOrderRequest {
        <<record>>
        +UUID userId
        +String symbol
        +String type
        +Integer quantity
        +BigDecimal price
    }
    class OrderResponse {
        <<record>>
        +UUID orderId
        +String status
        +String message
    }
    class OrderHistoryResponse {
        <<record>>
        +from(Order) OrderHistoryResponse$
    }
    class PortfolioResponse {
        <<record>>
        +Portfolio portfolio
        +List~Holding~ holdings
        +List~Transaction~ transactions
    }
    class PnlResponse {
        <<record>>
        +BigDecimal totalPnl
    }
    PortfolioController --> PlaceOrderUseCase : order command
    PortfolioController --> CancelOrderUseCase : cancel command
    PortfolioController --> GetPortfolioUseCase : portfolio query
    PortfolioController --> GetPnLUseCase : PnL query
    PortfolioController --> OrderResponseMapper : response mapping
    PortfolioController --> UserIdResolver : user context
    PortfolioController ..> PlaceOrderRequest : input
    PortfolioController ..> OrderResponse : output
    PortfolioController ..> OrderHistoryResponse : output
    PortfolioController ..> PortfolioResponse : output
    PortfolioController ..> PnlResponse : output
```

### 4.4 Application services

```mermaid
classDiagram
    class PlaceOrderService {
        +placeOrder(UUID, String, String, Integer) Order
        +placeOrder(UUID, String, String, Integer, BigDecimal) Order
    }
    class CancelOrderService {
        +cancelOrder(UUID, Optional) Order
    }
    class PortfolioService {
        +getPortfolio(UUID) Portfolio
        +getHoldings(UUID) List~Holding~
        +getTransactionHistory(UUID) List~Transaction~
        +getOrderHistory(UUID) List~Order~
        +getTotalPnl(UUID) BigDecimal
    }
    class PortfolioAccountService {
        +getOrCreate(UUID) Portfolio
        +getRequired(UUID) Portfolio
    }
    class OrderFactory {
        +pendingOrder(ValidatedOrderRequest, Portfolio) Order
    }
    class ValidatedOrderRequest {
        <<record>>
        +UUID userId
        +String symbol
        +String type
        +int quantity
        +BigDecimal price
    }
    class OrderConstants {
        <<utility>>
        +BigDecimal INITIAL_CASH$
        +BigDecimal DEFAULT_ORDER_PRICE$
        +String BUY$
        +String SELL$
        +String PENDING$
        +String CANCELLED$
    }

    PlaceOrderUseCase <|.. PlaceOrderService : command behavior
    CancelOrderUseCase <|.. CancelOrderService : command behavior
    GetPortfolioUseCase <|.. PortfolioService : query behavior
    GetPnLUseCase <|.. PortfolioService : query behavior

    PlaceOrderService --> OrderValidator : policy check
    PlaceOrderService --> PortfolioAccountService : account access
    PlaceOrderService --> OrderReservationStrategyRegistry : reservation policy
    PlaceOrderService --> OrderFactory : order creation
    PlaceOrderService --> OrderEventPublisher : domain event
    PlaceOrderService --> OrderRepository : state storage
    CancelOrderService --> OrderReservationStrategyRegistry : release policy
    CancelOrderService --> OrderEventPublisher : domain event
    CancelOrderService --> OrderRepository : state storage
    PortfolioService --> PortfolioAccountService : account access
    PortfolioService --> HoldingRepository : holding view
    PortfolioService --> TransactionRepository : trade view
    PortfolioService --> OrderRepository : order view
    PortfolioAccountService --> PortfolioRepository : account storage
    OrderFactory ..> ValidatedOrderRequest : source data
    OrderFactory ..> Order : created entity
    note for PortfolioService "getTotalPnl replays transactions with weighted-average cost (inner PositionCost)"
```

### 4.5 Validation subsystem

```mermaid
classDiagram
    class OrderValidator {
        <<interface>>
        +validate(UUID, String, String, Integer, BigDecimal) ValidatedOrderRequest
    }
    class DefaultOrderValidator {
        +validate(UUID, String, String, Integer, BigDecimal) ValidatedOrderRequest
    }
    class OrderValidationRule {
        <<interface>>
        +validate(UUID, String, String, Integer, BigDecimal) void
    }
    class BasicFormatValidationRule {
        +validate(UUID, String, String, Integer, BigDecimal) void
    }
    class TradingHoursValidationRule {
        -boolean tradingHoursEnabled
        -Clock clock
        +validate(UUID, String, String, Integer, BigDecimal) void
    }
    class PriceBandValidationRule {
        -boolean tradingHoursEnabled
        +validate(UUID, String, String, Integer, BigDecimal) void
    }
    class SymbolPriceCache {
        <<interface>>
        +put(String, BigDecimal) void
        +get(String) Optional~CachedPrice~
        +clear() void
    }
    class InMemorySymbolPriceCache {
        -Map cache
    }
    class CachedPrice {
        <<record>>
        +String symbol
        +BigDecimal price
        +BigDecimal floorPrice
        +BigDecimal ceilingPrice
        +LocalDateTime updatedAt
    }
    OrderValidator <|.. DefaultOrderValidator : implementation
    OrderValidationRule <|.. BasicFormatValidationRule : format policy
    OrderValidationRule <|.. TradingHoursValidationRule : time policy
    OrderValidationRule <|.. PriceBandValidationRule : price policy
    SymbolPriceCache <|.. InMemorySymbolPriceCache : cache implementation
    SymbolPriceCache .. CachedPrice : price snapshot
    DefaultOrderValidator o-- "1..*" OrderValidationRule : policy chain
    DefaultOrderValidator --> SymbolPriceCache : price context
    DefaultOrderValidator --> OrderRepository : price source
    PriceBandValidationRule --> SymbolPriceCache : price context
    DefaultOrderValidator ..> ValidatedOrderRequest : validated intent
    note for BasicFormatValidationRule "@Order(1): null/blank, symbol regex, quantity/price > 0"
    note for TradingHoursValidationRule "@Order(2): Mon-Fri, 09:00-11:30 and 13:00-15:00 (toggle trading.hours.enabled)"
    note for PriceBandValidationRule "@Order(3): price within [floor, ceiling], HOSE +/-7%"
```

### 4.6 Reservation subsystem

```mermaid
classDiagram
    class OrderReservationStrategy {
        <<interface>>
        +orderType() String
        +reserve(Portfolio, ValidatedOrderRequest) void
        +release(Order) void
    }
    class BuyOrderReservationStrategy {
        +orderType() String
        +reserve(Portfolio, ValidatedOrderRequest) void
        +release(Order) void
    }
    class SellOrderReservationStrategy {
        +orderType() String
        +reserve(Portfolio, ValidatedOrderRequest) void
        +release(Order) void
    }
    class OrderReservationStrategyRegistry {
        -Map strategiesByType
        +get(String) OrderReservationStrategy
    }
    OrderReservationStrategy <|.. BuyOrderReservationStrategy : buy policy
    OrderReservationStrategy <|.. SellOrderReservationStrategy : sell policy
    OrderReservationStrategyRegistry o-- "1..*" OrderReservationStrategy : policy registry
    BuyOrderReservationStrategy --> PortfolioRepository : cash state
    SellOrderReservationStrategy --> HoldingRepository : holding state
    note for OrderReservationStrategyRegistry "Map keyed by orderType (BUY/SELL); unknown type -> BadRequestException"
    note for BuyOrderReservationStrategy "BUY: freeze cash = price*qty (Conflict if insufficient); release = refund cash"
    note for SellOrderReservationStrategy "SELL: lock shares from holding; release = return shares"
```

### 4.7 Matching subsystem

```mermaid
classDiagram
    class OrderMatchProcessor {
        +matchPendingOrders(String, BigDecimal) void
        +processMatch(Order, BigDecimal) void
    }
    class OrderMatchStrategy {
        <<interface>>
        +orderType() String
        +match(Portfolio, Order, BigDecimal) void
    }
    class BuyOrderMatchStrategy {
        +orderType() String
        +match(Portfolio, Order, BigDecimal) void
    }
    class SellOrderMatchStrategy {
        +orderType() String
        +match(Portfolio, Order, BigDecimal) void
    }
    class OrderMatchStrategyRegistry {
        -Map strategiesByType
        +get(String) OrderMatchStrategy
    }
    OrderMatchStrategy <|.. BuyOrderMatchStrategy : buy policy
    OrderMatchStrategy <|.. SellOrderMatchStrategy : sell policy
    OrderMatchStrategyRegistry o-- "1..*" OrderMatchStrategy : policy registry
    OrderMatchProcessor --> OrderMatchStrategyRegistry : match policy
    OrderMatchProcessor --> OrderRepository : order state
    OrderMatchProcessor --> PortfolioRepository : portfolio state
    OrderMatchProcessor --> TransactionRepository : trade record
    OrderMatchProcessor --> PortfolioEventPublisher : domain event
    BuyOrderMatchStrategy --> PortfolioRepository : cash state
    BuyOrderMatchStrategy --> HoldingRepository : holding state
    SellOrderMatchStrategy --> PortfolioRepository : cash state
    SellOrderMatchStrategy --> HoldingRepository : holding state
    note for OrderMatchProcessor "loops PENDING orders for a symbol; BUY matches if order.price ≥ price, SELL if order.price ≤ price; on match: strategy.match + Transaction(FILLED) + order FILLED + publish; per-order try/catch"
    note for BuyOrderMatchStrategy "refund price improvement; recompute weighted avgPrice; quantity += qty"
    note for SellOrderMatchStrategy "add proceeds = price*qty; delete holding if qty == 0"
```

### 4.8 Outbound ports + messaging adapters

```mermaid
classDiagram
    class OrderEventPublisher {
        <<interface>>
        +publishOrderCreated(Order) void
        +publishOrderCancelled(Order) void
    }
    class PortfolioEventPublisher {
        <<interface>>
        +publishPortfolioUpdated(Portfolio, Order, BigDecimal) void
    }
    class RabbitOrderEventPublisher {
        -AmqpTemplate rabbitTemplate
        +publishOrderCreated(Order) void
        +publishOrderCancelled(Order) void
    }
    class RabbitPortfolioEventPublisher {
        -AmqpTemplate rabbitTemplate
        +publishPortfolioUpdated(Portfolio, Order, BigDecimal) void
    }
    class OrderEventPayload {
        <<record>>
        +UUID orderId
        +UUID userId
        +UUID portfolioId
        +String symbol
        +String type
        +BigDecimal price
        +Integer quantity
        +String status
        +LocalDateTime timestamp
    }
    class PortfolioUpdatedEvent {
        <<record>>
        +UUID portfolioId
        +UUID userId
        +String symbol
        +String transactionType
        +Integer quantity
        +BigDecimal price
        +LocalDateTime timestamp
    }
    OrderEventPublisher <|.. RabbitOrderEventPublisher : adapter
    PortfolioEventPublisher <|.. RabbitPortfolioEventPublisher : adapter
    RabbitOrderEventPublisher ..> OrderEventPayload : order event shape
    RabbitPortfolioEventPublisher ..> PortfolioUpdatedEvent : portfolio event shape
    note for RabbitOrderEventPublisher "to order.exchange, keys order.created / order.cancelled (failures logged, swallowed)"
    note for RabbitPortfolioEventPublisher "to portfolio.exchange, routing key updated"
```

### 4.9 Security

```mermaid
classDiagram
    class JwtTokenProvider {
        <<interface>>
        +validateToken(String) boolean
        +getUserIdFromToken(String) String
        +getRoleFromToken(String) String
        +getTokenType(String) String
    }
    class JwtTokenProviderImpl {
        -SecretKey secretKey
    }
    class OncePerRequestFilter {
        <<abstract>>
    }
    class JwtAuthenticationFilter {
        +doFilterInternal(request, response, chain) void
    }
    class SecurityConfig {
        <<Configuration>>
        +securityFilterChain(HttpSecurity) SecurityFilterChain
    }
    class UserIdResolver {
        +resolveCurrentUserId() UUID
    }
    JwtTokenProvider <|.. JwtTokenProviderImpl : implementation
    OncePerRequestFilter <|-- JwtAuthenticationFilter : filter type
    JwtAuthenticationFilter --> JwtTokenProvider : token service
    SecurityConfig --> JwtAuthenticationFilter : security chain
    note for JwtAuthenticationFilter "Bearer header; only type=access; sets SecurityContext(userId, role)"
    note for SecurityConfig "stateless; permit /actuator/**, /health; all else authenticated"
    note for UserIdResolver "reads SecurityContext authentication.name then UUID.fromString"
```

### 4.10 Error handling

```mermaid
classDiagram
    class RuntimeException
    class BadRequestException
    class ConflictException
    class NotFoundException
    class RestExceptionHandler {
        <<RestControllerAdvice>>
        +handleBadRequest(Exception) ResponseEntity
        +handleNotFound(NotFoundException) ResponseEntity
        +handleConflict(ConflictException) ResponseEntity
    }
    class ErrorResponse {
        <<record>>
        +String error
        +String message
    }
    RuntimeException <|-- BadRequestException : input error
    RuntimeException <|-- ConflictException : rule conflict
    RuntimeException <|-- NotFoundException : missing resource
    RestExceptionHandler ..> ErrorResponse : error shape
    RestExceptionHandler ..> BadRequestException : client error
    RestExceptionHandler ..> ConflictException : conflict error
    RestExceptionHandler ..> NotFoundException : not-found error
    note for RestExceptionHandler "BadRequest / IllegalArgument / MethodArgumentNotValid -> 400; NotFound -> 404; Conflict -> 409"
```

---

## 5. State machine — Order lifecycle

```mermaid
stateDiagram-v2
    [*] --> PENDING : order accepted
    PENDING --> FILLED : market match
    PENDING --> CANCELLED : user cancellation
    FILLED --> [*] : completed
    CANCELLED --> [*] : closed
    note right of PENDING
        Only PENDING orders can be
        cancelled or matched.
        @PrePersist sets status = PENDING.
    end note
```

---

## 6. Sequence diagrams

### 6.1 Place Order (`POST /portfolio/order`)

```mermaid
sequenceDiagram
    autonumber
    actor C as Frontend / Gateway
    participant F as Auth Boundary
    participant CT as API Adapter
    participant UR as User Context
    participant POS as Order Command Service
    participant V as Validation Policy
    participant PAS as Account Service
    participant PR as Portfolio Store
    participant RR as Reservation Policy Registry
    participant RS as Reservation Policy
    participant OF as Order Factory
    participant OR as Order Store
    participant EP as Event Publisher
    participant MQ as Message Broker

    C->>F: Place order request
    F->>F: Establish user context
    F->>CT: Authenticated request
    CT->>UR: Resolve actor
    UR-->>CT: Actor identity
    CT->>POS: Place order command

    POS->>V: Check order intent
    V->>V: Apply business rules
    break invalid input
        V-->>C: Reject request
    end
    V-->>POS: Valid order intent

    POS->>PAS: Ensure portfolio account
    PAS->>PR: Load or create account
    PR-->>PAS: Portfolio account
    PAS-->>POS: Account ready

    POS->>RR: Select reservation policy
    RR-->>POS: Reservation policy
    POS->>RS: Reserve assets
    break insufficient cash / holdings
        RS-->>C: Reject command
    end
    RS->>RS: Persist reservation

    POS->>OF: Create pending order
    OF-->>POS: Pending order
    POS->>OR: Store order
    OR-->>POS: Stored order
    POS->>EP: Publish order event
    EP->>MQ: Broadcast event
    POS-->>CT: Command result
    CT-->>C: Order accepted
```

### 6.2 Cancel Order (`DELETE /portfolio/order/{orderId}`)

```mermaid
sequenceDiagram
    autonumber
    actor C as Frontend / Gateway
    participant CT as API Adapter
    participant UR as User Context
    participant COS as Cancel Command Service
    participant OR as Order Store
    participant RR as Reservation Policy Registry
    participant RS as Reservation Policy
    participant EP as Event Publisher
    participant MQ as Message Broker

    C->>CT: Cancel order request
    CT->>UR: Resolve actor
    UR-->>CT: Actor identity
    CT->>COS: Cancel order command

    break invalid command
        COS-->>C: Reject request
    end
    COS->>OR: Load order
    OR-->>COS: Order state
    break order not found
        COS-->>C: Reject request
    end
    break order cannot be cancelled
        COS-->>C: Reject command
    end

    COS->>RR: Select release policy
    RR-->>COS: Release policy
    COS->>RS: Release reservation
    RS->>RS: Persist released assets
    COS->>OR: Mark order cancelled
    OR-->>COS: Cancelled order
    COS->>EP: Publish order event
    EP->>MQ: Broadcast event
    COS-->>CT: Command result
    CT-->>C: Cancellation accepted
```

### 6.3 Price Update → Order Matching (event-driven)

```mermaid
sequenceDiagram
    autonumber
    participant MKT as Market System
    participant MQ as Message Broker
    participant L as Price Event Adapter
    participant PC as Price Context
    participant OMP as Matching Service
    participant OR as Order Store
    participant PR as Portfolio Store
    participant MR as Matching Policy Registry
    participant MS as Matching Policy
    participant HR as Holding Store
    participant TR as Trade Store
    participant PEP as Event Publisher
    participant AI as AI Consumer

    MKT->>MQ: Market price changed
    MQ->>L: Deliver price event
    L->>L: Interpret price event
    L->>PC: Update price context
    L->>OMP: Start order matching
    OMP->>OR: Load pending candidates
    OR-->>OMP: Candidate orders

    loop each pending order
        OMP->>OMP: Evaluate match eligibility
        opt order can be filled
            OMP->>PR: Load portfolio
            PR-->>OMP: Portfolio state
            OMP->>MR: Select matching policy
            MR-->>OMP: Matching policy
            OMP->>MS: Settle order
            alt BUY
                MS->>PR: Update cash
                MS->>HR: Update holding
            else SELL
                MS->>PR: Update cash
                MS->>HR: Update holding
            end
            OMP->>TR: Record trade
            OMP->>OR: Close order
            OMP->>PEP: Publish portfolio event
            PEP->>MQ: Broadcast event
            MQ->>AI: Deliver portfolio update
        end
    end
    Note over OMP: Matching is isolated per order<br/>one failed match does not stop the loop
```

### 6.4 Get Portfolio & PnL (read flows)

```mermaid
sequenceDiagram
    autonumber
    actor C as Frontend / Gateway
    participant CT as API Adapter
    participant UR as User Context
    participant PS as Portfolio Query Service
    participant PAS as Account Service
    participant PR as Portfolio Store
    participant HR as Holding Store
    participant TR as Trade Store

    C->>CT: Portfolio read request
    CT->>UR: Resolve actor
    UR-->>CT: Actor identity
    CT->>PS: Build portfolio view
    PS->>PAS: Ensure account
    PAS->>PR: Load account
    PR-->>PAS: Portfolio account
    PAS-->>PS: Portfolio account
    PS-->>CT: Portfolio summary
    CT->>PS: Add holdings view
    PS->>HR: Load holdings
    HR-->>PS: Holdings
    PS-->>CT: Holdings view
    CT->>PS: Add trade view
    PS->>TR: Load trades
    TR-->>PS: Trade history
    PS-->>CT: Trade view
    CT-->>C: Portfolio response

    Note over C,TR: PnL follows the same read path<br/>then derives realized performance from trades
```

---

## 7. Activity diagrams

### 7.1 Place Order (decision flow)

```mermaid
flowchart TD
    A([Order request]) -->|enters service| B[Resolve actor]
    B -->|actor context| C{Authorized?}
    C -- No --> E400a[/Reject request/]
    C -- Yes --> D[Check order intent]
    D -->|business rules| V1{Intent valid?}
    V1 -- No --> E400b[/Reject request/]
    V1 -- Yes --> V2{Market rules allow?}
    V2 -- No --> E400b
    V2 -- Yes --> V3{Price acceptable?}
    V3 -- No --> E400b
    V3 -- Yes --> N[Prepare order intent]
    N -->|valid intent| P[Ensure portfolio account]
    P -->|account ready| T{Supported side?}
    T -- No --> E400c[/Reject request/]
    T -- BUY --> RB{Buying power available?}
    RB -- No --> E409a[/Reject command/]
    RB -- Yes --> RBy[Reserve cash]
    T -- SELL --> RS{Holdings available?}
    RS -- No --> E409b[/Reject command/]
    RS -- Yes --> RSy[Reserve shares]
    RBy -->|assets reserved| F[Create pending order]
    RSy -->|assets reserved| F
    F -->|order ready| S[Store order]
    S -->|state changed| PUB[Publish order event]
    PUB -->|complete| OK([Order accepted])
```

### 7.2 Order Matching (on price update)

```mermaid
flowchart TD
    S([Market price event]) -->|event received| P[Read price update]
    P -->|valid update| C[Update price context]
    C -->|matching context| Q[Find candidate orders]
    Q -->|candidate list| L{More candidates?}
    L -- No --> E([Done])
    L -- Yes --> M{Can fill now?}
    M -- No --> L
    M -- Yes --> G{Still open?}
    G -- No --> L
    G -- Yes --> EX[Apply match policy]
    EX -->|settled| TX[Record trade]
    TX -->|trade recorded| UO[Close order]
    UO -->|portfolio changed| PUB[Publish portfolio event]
    PUB -->|next candidate| L
    EX -. failure .-> ERR[Skip candidate]
    ERR -->|next candidate| L
```

---

## 8. Deployment diagram

```mermaid
flowchart TB
    subgraph client["Client tier"]
        BR["Client App"]
    end
    subgraph net["Docker network: stockwise"]
        GW["API Gateway"]
        subgraph psvc["portfolio-service container"]
            APPJ["Portfolio Service"]
        end
        MS["Market Service"]
        AIS["AI Service"]
        MQN(["Message Broker"])
        PG[("PostgreSQL")]
    end
    BR -->|user traffic| GW
    GW -->|portfolio traffic| APPJ
    APPJ -->|portfolio state| PG
    APPJ <-->|domain events| MQN
    MS -->|market events| MQN
    MQN -->|portfolio updates| AIS
    APPJ -. integration overview .-> note1["Event flow<br/>market -> portfolio<br/>portfolio -> ai<br/>portfolio -> subscribers"]
```

Inside the Docker network, services address each other by service name
(`postgres`, `rabbitmq`), never `localhost`. The `stock_prices` table read by
`OrderRepository.findLatestPriceBySymbol` is owned by the data-pipeline.
