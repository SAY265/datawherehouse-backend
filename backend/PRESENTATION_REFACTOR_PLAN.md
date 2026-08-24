# Kế hoạch chuẩn hóa tầng Presentation

## Phạm vi và kết luận audit

Đã đối chiếu toàn bộ file Python trong `backend/src/presentation/` với `TECHNICAL_CODING_GUIDELINES.md`, tập trung vào SRP, DRY, dependency rule, giới hạn kích thước, type hints, DTO/OpenAPI metadata, error envelope và composition root.

Phần API refactor bắt buộc đã xử lý ngay các điểm liên quan trực tiếp: route/resource mới, typed path contexts, proposal DTO về `dtos/`, DDL DTO thuộc Data Model, typed error response factory và `ApiResponseRoute` cho JSON success. Các cleanup độc lập bên dưới được giữ thành kế hoạch riêng để tránh mở rộng phạm vi triển khai.

## Kết quả theo nhóm quy tắc

| Nhóm | Hiện trạng | Kết luận |
| --- | --- | --- |
| Dependency rule | Router chỉ phụ thuộc Application contracts/DTO; Infrastructure chỉ xuất hiện trong `dependencies/` composition root | Đạt |
| Success envelope | Các JSON success route đang dùng `ApiResponseRoute` | Đạt |
| API mới | Route, operation ID, payload và error schema đã được chuẩn hóa theo resource | Đạt trong refactor hiện tại |
| SRP/composition | Data Model và Data Warehouse workflow đã có composition root riêng; process-scoped resources nằm riêng | Đạt trong refactor hiện tại |
| DRY | `ProjectAccessPolicy`, typed path context và error response map đã có provider/factory dùng chung | Đạt trong refactor hiện tại |
| Kích thước | `api/v1/data_sources.py` có 125 dòng vật lý; upload mapping và HTTP route concerns nên được tách trước khi logic tiếp tục tăng | Cần xử lý |
| Naming | `dtos/common.py` là tên chung chung bị guideline cấm | Chưa đạt |
| DTO organization | Cây `schemas/` trùng vai trò với `dtos/` đã được loại bỏ khi chuyển proposal response; Project vẫn còn nested requirement DTO lặp contract hiện có | Một phần chưa đạt |
| Type/doc metadata | `Any` ở error response đã được thay bằng TypedDict; một số DTO/endpoint cũ rỗng hoặc thiếu contract/docstring nên không thể chứng minh tuân thủ | Cần xử lý |
| Dead scaffolding | Baseline có 15 file Python rỗng | Chưa đạt |
| Fitness tests | Chưa có test tự động chặn import sai tầng, JSON route thiếu `ApiResponseRoute`, endpoint quá 3 tham số hoặc file Presentation quá giới hạn | Chưa đạt |

## Danh sách 15 file rỗng ở baseline

Hai file Data Model Change đã được tái sử dụng trong API refactor hiện tại. Mười ba file còn lại cần xóa nếu module chưa được triển khai, hoặc chỉ tạo lại khi có contract thật.

1. `api/v1/analytical_requirements.py`
2. `api/v1/auth.py`
3. `api/v1/sessions.py`
4. `api/v1/users.py`
5. `api/v1/workflows.py`
6. `dtos/analytical_requirements/request.py`
7. `dtos/analytical_requirements/response.py`
8. `dtos/auth/request.py`
9. `dtos/auth/response.py`
10. `dtos/data_model_changes/request.py` — đã chuyển thành typed path DTO.
11. `dtos/data_model_changes/response.py` — đã nhận proposal schema từ cây `schemas/`.
12. `dtos/sessions/request.py`
13. `dtos/sessions/response.py`
14. `dtos/users/request.py`
15. `dtos/users/response.py`

## Kế hoạch refactor

### P1 — Xóa dead scaffolding và hợp nhất DTO tree

- Xóa 13 file còn rỗng và các package/directory rỗng không được router đăng ký.
- Giữ duy nhất `presentation/dtos/`; không tạo lại cây `presentation/schemas/`.
- Đổi `dtos/common.py` thành `dtos/api_errors.py`, cập nhật import một lần tại routing/global handlers.
- Thay `ProjectRequirementResponse` bằng mapping/tái sử dụng `RequirementResponse` nếu OpenAPI composition không làm thay đổi public payload.

Tiêu chí hoàn tất: không còn file Python rỗng, không còn `schemas/`, không có module tên `common.py`, OpenAPI không đổi ngoài tên schema nội bộ đã chấp thuận.

### Hạng mục đã hoàn tất trong API refactor — Composition root

- Đã chuyển Data Warehouse workflow provider khỏi `dependencies/data_models.py` sang `dependencies/data_warehouse_workflows.py`.
- Đã tạo provider request-scoped duy nhất cho `ProjectAccessPolicy`; các Data Model, Data Source, Requirement, Project và Sandbox providers tái sử dụng provider này.
- Đã thay positional repository tuple bằng typed workflow repository bundle.
- `data_model_resources.py` chỉ còn giữ process-scoped validator/PII resources.

Tiêu chí hoàn tất: mỗi dependency module chỉ wire một application module, không lặp cách dựng access policy, không có positional repository tuple.

### P3 — Giảm kích thước và tham số endpoint

- Tách đọc `UploadFile` giới hạn kích thước khỏi `api/v1/data_sources.py` thành typed request dependency dành riêng cho batch upload.
- Dùng typed path/dependency contexts cho mọi endpoint có nguy cơ vượt ba tham số; không làm mất `Path`/`Query` descriptions trong OpenAPI.
- Baseline `sandbox.py` từng vượt 120 dòng logic và có hai endpoint vượt ba tham số; API refactor đã đưa file xuống dưới giới hạn và endpoint còn tối đa ba tham số. Thêm test để ngăn hồi quy.

Tiêu chí hoàn tất: file code thủ công không vượt 120 dòng logic, function không vượt 25 dòng logic, endpoint tối đa ba tham số.

### P4 — Hoàn thiện type và API documentation

- Rà từng request/response DTO cũ, bổ sung `Field` description/constraints và `extra="forbid"` ở request boundary.
- Bổ sung Google-style docstring cho public providers/mappers có side effect hoặc exception không hiển nhiên.
- Không dùng `Any`, `dict` hoặc domain entity làm public response khi có thể mô hình hóa cụ thể.
- Dùng typed `error_responses()` factory duy nhất; loại các map status/error copy-paste còn lại.

Tiêu chí hoàn tất: Ruff/type checker sạch, OpenAPI không có anonymous/untyped object ngoài dữ liệu preview vốn là map động có chủ đích.

### P5 — Architecture fitness tests

- AST test cấm Domain/Application import FastAPI/Pydantic/Infrastructure và cấm router import concrete service/repository.
- Route test yêu cầu mọi JSON success operation dùng `ApiResponseRoute`, có `operation_id`, response payload cụ thể và known error responses.
- AST/metrics test cảnh báo endpoint quá ba tham số, function quá 25 dòng logic, file Presentation quá 120 dòng logic và file Python rỗng.
- Contract test phát hiện DTO Project/Data Source/Requirement lặp field thay vì reuse application outputs/mappers.

Tiêu chí hoàn tất: fitness suite chạy trong CI cùng Ruff/Pytest và thất bại khi tái xuất hiện các vi phạm trên.

## Thứ tự triển khai đề xuất

1. P1 vì ít rủi ro và loại ambiguity về cấu trúc.
2. P3 và P4 theo từng resource, mỗi resource export OpenAPI và chạy contract tests ngay sau thay đổi.
3. P5 khóa các invariant kiến trúc sau khi code đã đạt chuẩn.

Không thay đổi Domain/Application business rule trong các phase này. Nếu phát hiện logic nghiệp vụ ở Presentation, di chuyển về abstraction hiện có ở Domain/Application; không sao chép hoặc viết lại rule tại HTTP boundary.
