# Market Service Documentation

## Mục tiêu thư mục này

Thư mục `docs/market-service` tập trung mô tả cách triển khai `market-service` dựa trên source code hiện tại của StockWise, không chỉ dựa trên tài liệu kế hoạch.

Bộ tài liệu này giúp team:
- hiểu rõ `market-service` hiện đang ở trạng thái nào
- biết luồng dữ liệu market hiện đi từ đâu đến đâu
- thống nhất API contract cần có cho frontend và service khác
- có lộ trình rõ ràng để chuyển service từ stub sang production-ready
- có checklist chạy thử, test và vận hành cục bộ

## Tóm tắt hiện trạng

Hiện tại `market-service` đã có nền tảng cấu trúc nhưng chưa hoàn thiện phần business logic:
- đã có Spring Boot service riêng ở `services/market-service`
- đã có controller cho 3 endpoint market chính
- đã có entity và repository cho `stock_prices` và `financial_ratios`
- đã có RabbitMQ config và listener cho `price.updated`
- nhưng `MarketService` vẫn đang trả mock data hardcode
- RabbitMQ listener hiện chỉ log message, chưa ghi DB hay refresh read model
- frontend chưa tích hợp `market-service`, vẫn dùng placeholder/mock data

## Tài liệu trong thư mục này

- [`current-state.md`](./current-state.md): phân tích cấu trúc và trạng thái thật của source hiện tại
- [`data-flow.md`](./data-flow.md): luồng dữ liệu từ data-pipeline đến market-service, frontend và portfolio-service
- [`api-contract.md`](./api-contract.md): contract đề xuất cho API market và mapping DTO
- [`implementation-plan.md`](./implementation-plan.md): lộ trình nâng cấp market-service từ stub sang production-ready
- [`testing-and-operations.md`](./testing-and-operations.md): cách chạy, kiểm thử và smoke test market-service

## Kết luận ngắn

Nếu nhìn vào source hiện tại, `market-service` nên được hiểu là một `read/query service` cho dữ liệu thị trường đã được ingest sẵn từ `data-pipeline`, thay vì một service tự fetch từ nguồn bên ngoài.

Điểm quan trọng nhất khi triển khai tiếp là:
1. thay `mock service` bằng truy vấn PostgreSQL thật
2. chuẩn hóa DTO và error contract
3. quyết định vai trò thật của RabbitMQ consumer trong `market-service`
4. tích hợp frontend với API market sau khi contract ổn định
