# Báo cáo thiết kế kiểm thử — Portfolio Service

> Phạm vi: phân tích cách **thiết kế** hai loại test đang có cho `portfolio-service`:
> 1. **Unit test** (Java / JUnit 5) — kiểm thử logic nghiệp vụ ở mức service, cô lập hoàn toàn.
> 2. **E2E / Integration test** (Python) — `scripts/e2e_portfolio_test.py`, kiểm thử toàn luồng qua hệ thống thật.
>
> Kiến trúc service là **hexagonal (ports & adapters)**, nên chiến lược test bám sát ranh giới
> port: unit test *mock outbound port*, E2E test *đi qua inbound adapter thật*.

---

## 1. Bức tranh tổng thể — Tháp kiểm thử (Test Pyramid)

Hai loại test phủ hai tầng khác nhau và **bổ sung cho nhau**, không trùng lặp:

```
        ╱╲          E2E (Python) — 1 file, 5 bước
       ╱  ╲         Chậm, cần Docker + Gateway + DB + RabbitMQ thật
      ╱────╲        Khẳng định: các service ghép lại CHẠY ĐÚNG với nhau
     ╱      ╲
    ╱  Unit  ╲      Unit (JUnit) — 3 file, 13 test
   ╱  (JUnit) ╲     Nhanh (mili-giây), không I/O
  ╱────────────╲    Khẳng định: từng nhánh logic nghiệp vụ ĐÚNG
```

| Tiêu chí | Unit test (Java) | E2E test (Python) |
| --- | --- | --- |
| Đối tượng | Application service đơn lẻ | Toàn hệ thống (gateway → service → DB → MQ) |
| Số lượng | 3 file, 13 test case | 1 script, 5 bước kịch bản |
| Phụ thuộc ngoài | Không (toàn bộ mock) | Có thật (HTTP, PostgreSQL, RabbitMQ) |
| Tốc độ | Mili-giây | Vài giây (có `sleep` chờ async) |
| Khi nào chạy | Mỗi lần `mvn test` / mỗi commit | Sau khi `docker compose up`, kiểm thử tích hợp |
| Phát hiện lỗi gì | Sai công thức, sai nhánh điều kiện | Sai hợp đồng API, sai luồng sự kiện, sai cấu hình |

---

## 2. Unit test (Java)

### 2.1. Công cụ & nền tảng

| Thành phần | Lựa chọn | Vai trò |
| --- | --- | --- |
| Test runner | **JUnit 5 (Jupiter)** — `@Test`, `@BeforeEach`, `@ExtendWith` | Vòng đời test |
| Mocking | **Mockito** — `@Mock`, `mock()`, `when()`, `verify()` | Giả lập outbound port |
| Assertion | **AssertJ** — `assertThat(...).isEqualByComparingTo(...)` | Khẳng định trôi chảy, dễ đọc |
| Nguồn dependency | `spring-boot-starter-test` (`pom.xml:78-82`) | Gói sẵn JUnit + Mockito + AssertJ |

Điểm quan trọng: **không có `@SpringBootTest`**. Các test này **không khởi động Spring context, không DB, không RabbitMQ** — chúng là unit test thuần, chạy trong mili-giây.

### 2.2. Triết lý thiết kế cốt lõi

Toàn bộ unit test tuân theo một khuôn mẫu nhất quán, khai thác đúng kiến trúc hexagonal:

1. **Mock các outbound port (repository / publisher)** — ranh giới ra ngoài (DB, message broker) bị cắt đứt và thay bằng mock.
2. **Dùng collaborator THẬT ở những nơi chứa logic cần kiểm thử** — validator, strategy, registry, factory, cache in-memory đều được `new` thật, không mock. Nhờ vậy test kiểm chứng *logic thật* chứ không phải hành vi giả lập.
3. **Kiểm chứng kép (state + interaction):**
   - *State verification*: khẳng định trạng thái entity sau khi gọi (vd `portfolio.getVirtualCash()` đã giảm).
   - *Interaction verification*: `verify(...)` khẳng định đúng port được gọi (vd `verify(orderEventPublisher).publishOrderCreated(...)`).
4. **Mẫu "save trả lại chính đối số"** để khẳng định trên entity bị mutate tại chỗ:
   ```java
   when(orderRepository.save(any(Order.class)))
       .thenAnswer(invocation -> invocation.getArgument(0));
   ```
   Cho phép lấy lại entity và assert trực tiếp lên nó.
5. **Tính xác định (determinism):** với logic phụ thuộc thời gian, test tiêm `Clock` cố định thay vì dùng giờ hệ thống.

### 2.3. Ba file unit test

#### a) `PortfolioServiceTest.java` — logic đọc & tính toán P/L

Cách dựng: dùng `mock()` trực tiếp (không cần `MockitoExtension`) vì chỉ cần vài mock đơn giản; `PortfolioAccountService` được `new` thật.

| Test | Mục tiêu thiết kế | Kỳ vọng |
| --- | --- | --- |
| `getTotalPnlReturnsZeroAfterBuyOnly` | Chỉ mua thì lãi/lỗ hiện thực = 0 | `0.00` |
| `getTotalPnlUsesAverageCostForRealizedSellProfit` | P/L hiện thực tính theo **giá vốn bình quân** (average cost) | `110.00` |
| `getOrderHistoryReturnsUserOrdersNewestFirstFromRepository` | Lịch sử lệnh trả đúng thứ tự repository (mới nhất trước) | `containsExactly(newest, oldest)` |

Điểm thiết kế đáng chú ý — bài toán P/L bình quân được dựng bằng 3 giao dịch có mốc thời gian (`day` 1→3) để buộc thuật toán phải xử lý đúng thứ tự: mua 3@100, mua 1@120, bán 2@160 → giá vốn bình quân = (3×100+1×120)/4 = 105 → lãi = (160−105)×2 = **110**.

#### b) `OrderServiceTest.java` — đặt lệnh & huỷ lệnh (`PlaceOrderService` + `CancelOrderService`)

Cách dựng (`@BeforeEach setUp`): tự tay **lắp ráp toàn bộ object graph** giống production — chuỗi validator (`BasicFormat` → `TradingHours` → `PriceBand`), registry chiến lược reservation (Buy/Sell), `OrderFactory` — chỉ repository và publisher là mock. Đây là kiểu *sociable unit test*: cô lập khỏi I/O nhưng vẫn chạy logic thật của các collaborator nội bộ.

| Test | Nhánh kiểm thử | Kỳ vọng then chốt |
| --- | --- | --- |
| `placeBuyOrderFreezesCashAndCreatesPendingOrder` | Mua → **đóng băng tiền** + chuẩn hoá symbol | cash 1000→800; `" fpt "`→`FPT`; status `PENDING`; phát event `OrderCreated` |
| `placeSellOrderFreezesHoldingAndCreatesPendingOrder` | Bán → **đóng băng cổ phiếu** | holding 10→6; status `PENDING`; publisher được gọi |
| `cancelPendingBuyOrderUnfreezesCash` | Huỷ lệnh chờ → **hoàn tiền** | cash 800→1000; status `CANCELLED`; `cancelledAt` ≠ null |
| `cancelRejectsNonPendingOrder` | Không cho huỷ lệnh đã khớp | ném `ConflictException` ("Only PENDING orders…") |
| `placeOrderRejectsUnsupportedTypeWithoutChangingAssets` | Loại lệnh sai → **không đụng tài sản** | ném `BadRequestException`; cash giữ nguyên 1000 |
| `placeBuyOrderRejectsPriceOutOfCeiling` | Giá vượt **trần biên độ ±7%** | ném `BadRequestException` ("out of the daily price band") |
| `placeBuyOrderRejectsPriceBelowFloor` | Giá dưới **sàn biên độ** | ném `BadRequestException` |
| `placeBuyOrderFailsOutsideTradingHours` | Ngoài **giờ/ngày giao dịch** | ném `BadRequestException` ("trading days") |

Hai kỹ thuật thiết kế nổi bật ở file này:
- **Kiểm thử negative path đi kèm khẳng định "không tác dụng phụ"** — không chỉ kiểm tra exception được ném, mà còn khẳng định tài sản *không bị thay đổi* (vd cash vẫn 1000), bảo vệ tính atomic của lệnh.
- **Tiêm `Clock` cố định để kiểm thử giờ giao dịch** — `placeBuyOrderFailsOutsideTradingHours` dựng `Clock.fixed(...)` trỏ vào **Chủ nhật 2026-06-07**, biến một quy tắc phụ thuộc lịch thành một test xác định, lặp lại được.

#### c) `PriceUpdateListenerAndMatchTest.java` — khớp lệnh theo sự kiện giá

Đây là test thú vị nhất về thiết kế: nó kiểm thử **listener tiêu thụ message RabbitMQ** mà **không cần RabbitMQ thật**. Cách làm là tạo thẳng đối tượng `org.springframework.amqp.core.Message` từ chuỗi JSON byte và gọi trực tiếp `onPriceUpdate(...)`.

| Test | Kịch bản | Logic được khẳng định |
| --- | --- | --- |
| `…MatchesPendingBuyOrder` | JSON dùng key `"price"`; lệnh mua 105 ≥ giá khớp 100 | **Hoàn chênh lệch** (105−100)×2 = 10 → cash 1000→1010; tạo holding; order→`FILLED`; lưu transaction; phát `portfolio.updated` |
| `…MatchesPendingSellOrder` | JSON dùng key `"close"`; lệnh bán 95 ≤ giá khớp 100 | **Thu tiền** 100×4 = 400 → cash 1000→1400; **xoá holding rỗng**; order→`FILLED`; phát `portfolio.updated` |

Điểm thiết kế:
- **Kiểm thử song song hai định dạng payload** (`price` và `close`) — chứng minh listener parse linh hoạt được nhiều schema message đầu vào.
- **Khẳng định toàn bộ chuỗi tác dụng phụ của một lần khớp lệnh** trong một test: cập nhật cache giá → cập nhật tiền/holding → đổi trạng thái order → ghi transaction → phát sự kiện. Một test bao trọn một "đơn vị hành vi nghiệp vụ".
- **Xác minh giá trị event phát ra** bằng `eq(...)`: `publishPortfolioUpdated(eq(portfolio), eq(buyOrder), eq(new BigDecimal("100.00")))` — bảo đảm đúng hợp đồng sự kiện gửi sang `ai-service`.

### 2.4. Đặc điểm chung của tầng unit test
- **So sánh tiền tệ bằng `isEqualByComparingTo`** thay vì `equals` — tránh bẫy `BigDecimal("800.00") != BigDecimal("800")` (khác scale).
- **Dữ liệu test dựng bằng helper factory riêng** (`portfolio(...)`, `order(...)`, `transaction(...)`, `holding(...)`) — giảm lặp, làm rõ ý đồ từng test.
- **Mỗi test một hành vi** — tên test mô tả đúng kỳ vọng (given/when/then ngầm trong tên).

---

## 3. E2E / Integration test (Python) — `scripts/e2e_portfolio_test.py`

### 3.1. Môi trường & công cụ

| Thành phần | Lựa chọn | Ghi chú |
| --- | --- | --- |
| Ngôn ngữ | Python (asyncio) | `async def main()` + `asyncio.run` |
| HTTP client | `urllib.request` + **`http.cookiejar`** | Thư viện chuẩn, không cần cài thêm |
| Message broker | `app.rabbitmq.producer.RabbitMQProducer` (`sys.path.append("/app")`) | Tái dùng **producer thật** của data-pipeline |
| Điểm vào hệ thống | `http://api-gateway:8080` | Gọi **service name** trong mạng Docker, đúng quy ước dự án |
| Tài khoản | `DEV_ADMIN_EMAIL` / `DEV_ADMIN_PASSWORD` (env, có default) | Đăng nhập admin seed sẵn |

Khác biệt nền tảng so với unit test: script này **chạy bên trong mạng Docker** (gọi `api-gateway`, `rabbitmq` bằng tên service, không phải `localhost`) và **tác động lên hệ thống thật**: gateway xác thực JWT, portfolio-service xử lý, PostgreSQL lưu, RabbitMQ vận chuyển sự kiện.

### 3.2. Triết lý thiết kế cốt lõi

1. **Kiểm thử qua hợp đồng API công khai (black-box)** — chỉ tương tác qua HTTP endpoint thật (`/auth/login`, `/portfolio`, `/portfolio/order`, `/portfolio/pnl`), không chạm vào nội bộ service. Đây là góc nhìn của client thật.
2. **Kích hoạt luồng bất đồng bộ bằng cách bơm sự kiện thật** — thay vì gọi API "khớp lệnh", script **publish message `price.updated` vào `market.exchange`** rồi `sleep(2)` chờ listener xử lý. Điều này kiểm thử đúng kiến trúc event-driven: lệnh chỉ khớp khi có sự kiện giá tới.
3. **Oracle tính lại độc lập phía client** — với mỗi bước, script *tự tính lại* giá trị kỳ vọng (tiền, số lượng, giá bình quân, P/L) từ dữ liệu nó quan sát được, rồi so với kết quả backend trả về. Đặc biệt ở bước P/L (dòng 237–257), script **mô phỏng lại đúng thuật toán average-cost** của backend từ lịch sử giao dịch — một oracle độc lập kiểm chứng tính đúng đắn.
4. **So sánh số thực có dung sai** — `abs(actual − expected) < 1.0` (1 VND), tránh sai số dấu phẩy động khi tính giá bình quân.
5. **Fail-fast, báo cáo rõ ràng** — mỗi bước in baseline/kết quả/kỳ vọng; sai thì `sys.exit(1)` hoặc `assert` dừng ngay, kèm thông điệp lệch giá trị.

### 3.3. Năm bước kịch bản

| Bước | Tên | Hành động | Bất biến được kiểm chứng |
| --- | --- | --- | --- |
| 1 | **Login** | `POST /auth/login` | Lấy được `accessToken`; status 200 |
| 2 | **Baseline** | `GET /portfolio` | Chụp ảnh tiền, số lượng FPT, giá vốn ban đầu làm mốc |
| 3 | **Đặt & huỷ lệnh** | `POST /portfolio/order` (BUY) rồi `DELETE /portfolio/order/{id}` | Đặt lệnh **giữ chỗ tiền** (cash giảm 10×125.000); huỷ thì **hoàn tiền** về đúng baseline |
| 4 | **Mua + cải thiện giá** | BUY @135.000 rồi publish giá khớp @130.000 | Khớp ở **giá thị trường thấp hơn** (130.000), không phải giá đặt; cash, số lượng, **giá vốn bình quân** đúng |
| 5 | **Bán + P/L hiện thực** | Lấy P/L gốc → SELL → publish giá → đọc lại | Cash tăng đúng tiền bán; số lượng giảm; **P/L hiện thực** khớp oracle average-cost |

Bước 4 và 5 là phần thể hiện rõ nhất giá trị của E2E: chúng kiểm chứng **vòng tròn đầy đủ** mà unit test không chạm tới — `POST order` (HTTP) → reserve (DB) → publish `price.updated` (RabbitMQ) → listener tiêu thụ → khớp lệnh → cập nhật DB → `GET /portfolio` đọc lại. Nếu sai cấu hình exchange, routing key, hay serialize message, unit test vẫn xanh nhưng E2E sẽ đỏ.

### 3.4. Kỹ thuật đáng chú ý
- **Quản lý phiên bằng cookie jar + Bearer token kết hợp** — `OPENER` giữ cookie tự động, đồng thời gắn `Authorization: Bearer` cho mỗi request.
- **Tái dùng producer thật của hệ thống** (`from app.rabbitmq.producer import RabbitMQProducer`) — message bơm vào có **đúng định dạng production**, không phải mock thủ công, nên test cả lớp serialize.
- **Payload `price.updated` đúng schema thật**: `symbol`, `price`, `source`, `timestamp` (ISO-8601 UTC), `action` — khớp hợp đồng RabbitMQ ở `CLAUDE.md` (`market.exchange` / `price.updated`).

---

## 4. So sánh & vai trò bổ trợ

| Khía cạnh | Unit test (JUnit) | E2E test (Python) |
| --- | --- | --- |
| Góc nhìn | White-box, nội bộ service | Black-box, client thật |
| Cô lập | Mock mọi outbound port | Không mock — dùng hạ tầng thật |
| Bất đồng bộ | Gọi listener trực tiếp (đồng bộ hoá) | Publish event thật + `sleep` chờ |
| Oracle kỳ vọng | Hằng số tính tay trong test | Tính lại động từ dữ liệu quan sát |
| So sánh số | `isEqualByComparingTo` (chính xác) | Dung sai `< 1.0` (float) |
| Bắt được lỗi | Sai logic, sai công thức, sai nhánh | Sai hợp đồng API/event, sai cấu hình MQ/DB, sai wiring giữa service |
| Điểm yếu | Không thấy lỗi tích hợp/cấu hình | Chậm, cần Docker, khó pin-point lỗi |

**Kết luận:** hai loại bổ sung nhau theo đúng tinh thần tháp kiểm thử. Unit test trả lời *"từng mảnh logic có đúng không?"* với tốc độ cao và độ chính xác cao; E2E test trả lời *"ghép tất cả lại, hệ thống có chạy đúng end-to-end không?"*. Một bug như "khớp lệnh dùng giá đặt thay vì giá thị trường" có thể lọt qua unit test của một module nhưng sẽ bị bước 4 của E2E bắt được.

---

## 5. Cách chạy

**Unit test (trong `services/portfolio-service/`):**
```bash
mvn test          # chạy toàn bộ unit test
mvn package       # build + test (theo Pre-PR checks của dự án)
```

**E2E test** — chạy *bên trong* mạng Docker sau khi `docker compose up`:
```bash
# Chạy từ một container có thể truy cập api-gateway & rabbitmq theo service name
python scripts/e2e_portfolio_test.py
```
Yêu cầu: gateway, portfolio-service, PostgreSQL, RabbitMQ đang chạy; tài khoản admin seed sẵn; biến môi trường `DEV_ADMIN_EMAIL` / `DEV_ADMIN_PASSWORD` (mặc định `admin@stockwise.local` / `password123`).

---

## 6. Nhận xét & khoảng trống

**Điểm mạnh của thiết kế hiện tại:**
- Unit test phủ tốt cả happy path lẫn negative path (biên độ giá, giờ giao dịch, loại lệnh sai, huỷ lệnh sai trạng thái) và **khẳng định cả "không tác dụng phụ"** khi lỗi.
- E2E test kiểm chứng đúng các bất biến tài chính quan trọng nhất (giữ chỗ/hoàn tiền, khớp giá thị trường, P/L bình quân) qua hạ tầng thật.
- Cả hai dùng oracle tính toán rõ ràng, không phải "chạy được là pass".

**Khoảng trống có thể cân nhắc (không nằm trong phạm vi báo cáo, chỉ ghi nhận):**
- E2E phụ thuộc `sleep(2)` cố định để chờ async — có thể không ổn định (flaky) khi máy chậm; cân nhắc cơ chế poll-until-condition có timeout.
- E2E giả định trạng thái khởi đầu nhất định (tài khoản admin, holding FPT) — chạy lặp lại sẽ tích luỹ trạng thái nếu không reset DB.
- Chưa có integration test ở mức Spring (`@SpringBootTest` + Testcontainers) làm tầng trung gian giữa unit và E2E full-stack.
