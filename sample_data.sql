--
-- Dữ liệu mẫu (Sample/Seed Data) cho hệ thống
-- Multi-Agent AI tạo Data Warehouse từ Business Requirement & Data Source
--
-- Áp dụng cho schema: database_schema.sql (PostgreSQL)
-- Kịch bản minh họa chính: VIMES Patient Record - Kho dữ liệu Hồ sơ bệnh án lưu trữ
--   (theo cấu trúc trong VIMES_Patient_Record_Cau_truc_du_lieu_2.xlsx)
-- Ngoài ra có thêm 9 project domain khác (Ngân hàng, Bán lẻ, Logistics, Giáo dục,
-- Sản xuất, Bảo hiểm, Viễn thông, Thương mại điện tử) để dữ liệu mẫu đa dạng,
-- đầy đủ các trạng thái/loại dữ liệu.
--
-- Cách dùng:
--   1) Chạy database_schema.sql trước để tạo schema.
--   2) Chạy file này để nạp dữ liệu mẫu:
--        psql -U postgres -d your_db -f sample_data.sql
--
-- Thứ tự insert tuân theo thứ tự phụ thuộc khóa ngoại (FK) trong schema:
--   users -> projects -> project_members -> requirements -> analytical_requirements
--   -> data_sources -> project_sessions -> session_events
--   -> data_models -> data_model_changes
--

BEGIN;

-- ============================================================
-- 1. USERS
-- ============================================================
INSERT INTO public.users (username, email, id, created_at, updated_at) VALUES
  ('annv', 'an.nguyen@dataworks.vn', 'a678ac27-3077-5ef2-8919-5218b2e48791', '2025-11-02 08:15:00+07'::timestamptz, '2025-11-02 08:15:00+07'::timestamptz),
  ('binhtt', 'binh.tran@dataworks.vn', '729525be-38aa-50fd-8ea9-3fedf76615f1', '2025-11-03 09:20:00+07'::timestamptz, '2025-11-03 09:20:00+07'::timestamptz),
  ('longlh', 'long.le@dataworks.vn', '0740e12f-bc1c-556f-9cc7-3ec5332e692e', '2025-11-05 10:05:00+07'::timestamptz, '2025-11-05 10:05:00+07'::timestamptz),
  ('huongpt', 'huong.pham@dataworks.vn', '15c1be82-ea36-5205-af17-7fb5947c2027', '2025-11-06 14:40:00+07'::timestamptz, '2025-11-06 14:40:00+07'::timestamptz),
  ('ducmh', 'duc.hoang@dataworks.vn', 'c0445430-562e-5472-bea6-06f3a5d6f645', '2025-11-10 08:00:00+07'::timestamptz, '2025-11-10 08:00:00+07'::timestamptz),
  ('lanvt', 'lan.vu@dataworks.vn', '4c507932-ae90-57a1-8765-885e45eba112', '2025-11-12 11:25:00+07'::timestamptz, '2025-11-12 11:25:00+07'::timestamptz),
  ('baodq', 'bao.dang@dataworks.vn', '85651d6b-4cc0-56ba-ba15-ffc404f10abc', '2025-11-15 13:50:00+07'::timestamptz, '2025-11-15 13:50:00+07'::timestamptz),
  ('ngocbt', 'ngoc.bui@dataworks.vn', 'e892c55a-77c6-5c8f-8e00-00da20839ba9', '2025-11-20 09:10:00+07'::timestamptz, '2025-11-20 09:10:00+07'::timestamptz),
  ('tungnv', 'tung.ngo@dataworks.vn', '25a6f954-f1cd-567d-88a0-630c4407b254', '2025-12-01 08:30:00+07'::timestamptz, '2025-12-01 08:30:00+07'::timestamptz),
  ('maidt', 'mai.do@dataworks.vn', '187ebbb4-aff9-555e-93e8-84718180c565', '2025-12-05 15:45:00+07'::timestamptz, '2025-12-05 15:45:00+07'::timestamptz);

-- ============================================================
-- 2. PROJECTS
-- ============================================================
INSERT INTO public.projects (name, description, domain, requirement, status, user_id, id, created_at, updated_at) VALUES
  ('VIMES - Kho dữ liệu Hồ sơ bệnh án lưu trữ', 'Xây dựng Data Warehouse tổng hợp dữ liệu hồ sơ bệnh án lưu trữ từ hệ thống VIMES Patient Record nhằm phân tích số lượng hồ sơ, tình trạng lưu trữ, thời gian điều trị và hiệu suất sử dụng kho/tủ/ngăn.', 'Y tế', 'Bệnh viện cần một kho dữ liệu tổng hợp thông tin hồ sơ bệnh án đã lưu trữ (Hồ sơ lưu trữ, Thông tin bệnh nhân, Danh sách bệnh nhân) để ban giám đốc theo dõi số lượng hồ sơ nhập/xuất kho theo tháng, tỷ lệ lấp đầy của từng Kho/Tủ/Ngăn, thời gian lưu trữ trung bình theo khoa, đồng thời đảm bảo dữ liệu cá nhân bệnh nhân được ẩn danh trước khi đưa vào các báo cáo phân tích.', 'ACTIVE', 'a678ac27-3077-5ef2-8919-5218b2e48791', '7e621a51-f48a-53bf-927d-f415ae6c9249', '2025-11-04 09:00:00+07'::timestamptz, '2026-08-10 16:20:00+07'::timestamptz),
  ('VIMES - Phân tích lượt khám & chẩn đoán', 'Data mart phân tích lượt khám bệnh, chẩn đoán và đối tượng chi trả viện phí theo khoa/phòng.', 'Y tế', 'Phòng Kế hoạch tổng hợp cần theo dõi số lượt bệnh nhân vào/ra theo từng khoa, phân bố chẩn đoán phổ biến, tỷ lệ bệnh nhân theo đối tượng chi trả (BHYT, Viện phí, Dịch vụ) theo từng quý để phục vụ báo cáo Sở Y tế.', 'ANALYZING', 'a678ac27-3077-5ef2-8919-5218b2e48791', '84bdeb46-0eba-564e-8437-833ede4e2718', '2025-12-10 10:00:00+07'::timestamptz, '2025-12-10 10:00:00+07'::timestamptz),
  ('Kho dữ liệu Ngân hàng bán lẻ', 'Data Warehouse tổng hợp giao dịch, tài khoản khách hàng phục vụ phân tích rủi ro tín dụng.', 'Ngân hàng', 'Khối Quản trị rủi ro cần một kho dữ liệu hợp nhất từ Core Banking và CRM để phân tích hành vi giao dịch bất thường, tính điểm tín dụng khách hàng theo thời gian thực và tuân thủ quy định về bảo mật dữ liệu tài chính cá nhân.', 'ACTIVE', '729525be-38aa-50fd-8ea9-3fedf76615f1', 'b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', '2025-11-08 08:30:00+07'::timestamptz, '2026-08-05 14:10:00+07'::timestamptz),
  ('Kho dữ liệu Bán lẻ - Chuỗi siêu thị', 'Tổng hợp dữ liệu bán hàng đa kênh (POS, e-commerce) để phân tích doanh thu và tồn kho.', 'Bán lẻ', 'Chuỗi siêu thị mong muốn hợp nhất dữ liệu bán hàng từ hệ thống POS tại 120 cửa hàng và sàn thương mại điện tử để phân tích doanh thu theo ngành hàng/khu vực, dự báo nhu cầu tồn kho và đo lường hiệu quả chương trình khuyến mãi theo tuần.', 'ACTIVE', '0740e12f-bc1c-556f-9cc7-3ec5332e692e', '54505703-ca04-5613-9f4a-d2499f12ee3d', '2025-11-11 09:15:00+07'::timestamptz, '2025-11-11 09:15:00+07'::timestamptz),
  ('Kho dữ liệu Vận hành Logistics', 'Data Warehouse theo dõi vận đơn, thời gian giao hàng và hiệu suất tài xế.', 'Logistics', 'Bộ phận vận hành cần theo dõi tỷ lệ giao hàng đúng hạn, thời gian trung chuyển trung bình giữa các kho vùng, hiệu suất từng tài xế/đối tác vận chuyển nhằm tối ưu chi phí logistics hàng tháng.', 'ACTIVE', 'c0445430-562e-5472-bea6-06f3a5d6f645', '18525676-8c6b-552b-8de7-a50899ef4b92', '2025-11-18 11:00:00+07'::timestamptz, '2025-11-18 11:00:00+07'::timestamptz),
  ('Kho dữ liệu Giáo dục - Trường Đại học', 'Tổng hợp dữ liệu tuyển sinh, học vụ và kết quả học tập sinh viên.', 'Giáo dục', 'Phòng Đào tạo cần kho dữ liệu tổng hợp điểm tuyển sinh, tiến độ học tập và tỷ lệ tốt nghiệp theo từng khoa/ngành để hỗ trợ ra quyết định phân bổ chỉ tiêu tuyển sinh hàng năm.', 'ANALYZING', '15c1be82-ea36-5205-af17-7fb5947c2027', '8dfcb679-8243-5be9-b8ee-b2bde7997277', '2025-12-02 08:45:00+07'::timestamptz, '2025-12-02 08:45:00+07'::timestamptz),
  ('Kho dữ liệu Sản xuất - Nhà máy', 'Theo dõi sản lượng, tỷ lệ lỗi và hiệu suất dây chuyền sản xuất (OEE).', 'Sản xuất', 'Nhà máy cần một kho dữ liệu tổng hợp từ hệ thống MES và cảm biến IoT để tính chỉ số OEE theo từng dây chuyền, phân tích nguyên nhân dừng máy và tỷ lệ sản phẩm lỗi theo ca làm việc.', 'ACTIVE', '4c507932-ae90-57a1-8765-885e45eba112', 'ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48', '2025-12-08 13:00:00+07'::timestamptz, '2025-12-08 13:00:00+07'::timestamptz),
  ('Kho dữ liệu Bảo hiểm nhân thọ', 'Phân tích hồ sơ hợp đồng, yêu cầu bồi thường và rủi ro gian lận.', 'Bảo hiểm', 'Công ty bảo hiểm cần hợp nhất dữ liệu hợp đồng, hồ sơ yêu cầu bồi thường (claim) và lịch sử thanh toán để phát hiện sớm các dấu hiệu gian lận bảo hiểm và tính tỷ lệ bồi thường theo sản phẩm.', 'ARCHIVED', '85651d6b-4cc0-56ba-ba15-ffc404f10abc', '53774151-12ea-53d4-9d34-ebccfd4a2594', '2025-10-20 08:00:00+07'::timestamptz, '2025-12-01 10:00:00+07'::timestamptz),
  ('Kho dữ liệu Viễn thông - Thuê bao', 'Tổng hợp dữ liệu cước, lưu lượng và tỷ lệ rời mạng (churn) của thuê bao.', 'Viễn thông', 'Bộ phận Chăm sóc khách hàng cần theo dõi lưu lượng data/thoại sử dụng, doanh thu ARPU và dự báo tỷ lệ rời mạng theo từng gói cước nhằm xây dựng chương trình giữ chân khách hàng.', 'ACTIVE', 'e892c55a-77c6-5c8f-8e00-00da20839ba9', 'f8c4432f-0252-5275-a581-958039b98639', '2025-12-15 09:30:00+07'::timestamptz, '2025-12-15 09:30:00+07'::timestamptz),
  ('Kho dữ liệu Thương mại điện tử', 'Data Warehouse phân tích hành vi mua sắm, giỏ hàng bỏ dở và hiệu quả marketing.', 'Thương mại điện tử', 'Sàn thương mại điện tử cần kho dữ liệu hợp nhất hành vi duyệt web, giỏ hàng, đơn hàng và chi phí quảng cáo để tối ưu tỷ lệ chuyển đổi và phân khúc khách hàng theo giá trị vòng đời (CLV).', 'ACTIVE', '25a6f954-f1cd-567d-88a0-630c4407b254', '6268eced-f86b-5e52-b0a9-262a806879e9', '2026-01-05 10:00:00+07'::timestamptz, '2026-01-05 10:00:00+07'::timestamptz);

-- ============================================================
-- 3. PROJECT_MEMBERS
-- ============================================================
INSERT INTO public.project_members (project_id, user_id, role, joined_at, id, created_at, updated_at) VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'a678ac27-3077-5ef2-8919-5218b2e48791', 'OWNER', '2025-11-04 09:05:00+07'::timestamptz, '154b2a3f-475b-5b7d-968a-ea7a72418443', '2025-11-04 09:05:00+07'::timestamptz, '2025-11-04 09:05:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', '15c1be82-ea36-5205-af17-7fb5947c2027', 'MEMBER', '2025-11-04 09:05:00+07'::timestamptz, 'fcbc80ec-30f7-5b69-ba9b-64901b5a1a2a', '2025-11-04 09:05:00+07'::timestamptz, '2025-11-04 09:05:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'e892c55a-77c6-5c8f-8e00-00da20839ba9', 'MEMBER', '2025-11-04 09:05:00+07'::timestamptz, '1e5e7b3b-2ae1-59e9-b37a-885435a332a5', '2025-11-04 09:05:00+07'::timestamptz, '2025-11-04 09:05:00+07'::timestamptz),
  ('84bdeb46-0eba-564e-8437-833ede4e2718', 'a678ac27-3077-5ef2-8919-5218b2e48791', 'OWNER', '2025-12-10 10:05:00+07'::timestamptz, '6456a3f4-67af-5e09-b466-ed4b71356659', '2025-12-10 10:05:00+07'::timestamptz, '2025-12-10 10:05:00+07'::timestamptz),
  ('84bdeb46-0eba-564e-8437-833ede4e2718', '4c507932-ae90-57a1-8765-885e45eba112', 'MEMBER', '2025-12-10 10:05:00+07'::timestamptz, '1b6f9efb-4e2c-588b-b616-385ed10e7275', '2025-12-10 10:05:00+07'::timestamptz, '2025-12-10 10:05:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', '729525be-38aa-50fd-8ea9-3fedf76615f1', 'OWNER', '2025-11-08 08:35:00+07'::timestamptz, 'e45fc8fe-bd81-54a7-b23c-d703c9d11b17', '2025-11-08 08:35:00+07'::timestamptz, '2025-11-08 08:35:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', '0740e12f-bc1c-556f-9cc7-3ec5332e692e', 'MEMBER', '2025-11-08 08:35:00+07'::timestamptz, '8cbc4908-2cb3-5a02-ac17-dded2427e7b1', '2025-11-08 08:35:00+07'::timestamptz, '2025-11-08 08:35:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', '187ebbb4-aff9-555e-93e8-84718180c565', 'MEMBER', '2025-11-08 08:35:00+07'::timestamptz, '05a4c217-1f2a-5854-aa76-875725a75a5e', '2025-11-08 08:35:00+07'::timestamptz, '2025-11-08 08:35:00+07'::timestamptz),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d', '0740e12f-bc1c-556f-9cc7-3ec5332e692e', 'OWNER', '2025-11-11 09:20:00+07'::timestamptz, '47332eb3-b621-5218-a543-df79240c77e9', '2025-11-11 09:20:00+07'::timestamptz, '2025-11-11 09:20:00+07'::timestamptz),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d', '25a6f954-f1cd-567d-88a0-630c4407b254', 'MEMBER', '2025-11-11 09:20:00+07'::timestamptz, 'c150d962-f99b-5f83-953e-8715650fe5e0', '2025-11-11 09:20:00+07'::timestamptz, '2025-11-11 09:20:00+07'::timestamptz),
  ('18525676-8c6b-552b-8de7-a50899ef4b92', 'c0445430-562e-5472-bea6-06f3a5d6f645', 'OWNER', '2025-11-18 11:05:00+07'::timestamptz, '036172d2-eb4f-51d5-b91f-bd0ff2cc4a30', '2025-11-18 11:05:00+07'::timestamptz, '2025-11-18 11:05:00+07'::timestamptz),
  ('18525676-8c6b-552b-8de7-a50899ef4b92', '85651d6b-4cc0-56ba-ba15-ffc404f10abc', 'MEMBER', '2025-11-18 11:05:00+07'::timestamptz, '9d9ec7e0-e622-51e5-bcef-925c75431f6d', '2025-11-18 11:05:00+07'::timestamptz, '2025-11-18 11:05:00+07'::timestamptz),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277', '15c1be82-ea36-5205-af17-7fb5947c2027', 'OWNER', '2025-12-02 08:50:00+07'::timestamptz, '6daf50ac-083f-5960-b651-46e383e80453', '2025-12-02 08:50:00+07'::timestamptz, '2025-12-02 08:50:00+07'::timestamptz),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277', '729525be-38aa-50fd-8ea9-3fedf76615f1', 'MEMBER', '2025-12-02 08:50:00+07'::timestamptz, '573f762b-4db4-53ea-bb20-db077c82ec2e', '2025-12-02 08:50:00+07'::timestamptz, '2025-12-02 08:50:00+07'::timestamptz),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48', '4c507932-ae90-57a1-8765-885e45eba112', 'OWNER', '2025-12-08 13:05:00+07'::timestamptz, 'a8a0ecd6-31ee-5f33-b333-59838740d3c7', '2025-12-08 13:05:00+07'::timestamptz, '2025-12-08 13:05:00+07'::timestamptz),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48', 'c0445430-562e-5472-bea6-06f3a5d6f645', 'MEMBER', '2025-12-08 13:05:00+07'::timestamptz, '670d9866-7d80-5d13-8234-d226400dfc50', '2025-12-08 13:05:00+07'::timestamptz, '2025-12-08 13:05:00+07'::timestamptz),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594', '85651d6b-4cc0-56ba-ba15-ffc404f10abc', 'OWNER', '2025-10-20 08:05:00+07'::timestamptz, '7c98993f-ee0e-5a1d-8ea6-d3859261598f', '2025-10-20 08:05:00+07'::timestamptz, '2025-10-20 08:05:00+07'::timestamptz),
  ('f8c4432f-0252-5275-a581-958039b98639', 'e892c55a-77c6-5c8f-8e00-00da20839ba9', 'OWNER', '2025-12-15 09:35:00+07'::timestamptz, 'c2460bb5-0b9f-5e80-bcfc-3c3e58b699fc', '2025-12-15 09:35:00+07'::timestamptz, '2025-12-15 09:35:00+07'::timestamptz),
  ('f8c4432f-0252-5275-a581-958039b98639', '187ebbb4-aff9-555e-93e8-84718180c565', 'MEMBER', '2025-12-15 09:35:00+07'::timestamptz, 'bd3f7b3d-6ef2-5cb4-a7d0-141693c6cc8d', '2025-12-15 09:35:00+07'::timestamptz, '2025-12-15 09:35:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', '25a6f954-f1cd-567d-88a0-630c4407b254', 'OWNER', '2026-01-05 10:05:00+07'::timestamptz, '28875f6d-1910-5196-90aa-9544cdc604aa', '2026-01-05 10:05:00+07'::timestamptz, '2026-01-05 10:05:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', '4c507932-ae90-57a1-8765-885e45eba112', 'MEMBER', '2026-01-05 10:05:00+07'::timestamptz, '78f81e8d-d5a2-5ba6-a0e7-6339edc67657', '2026-01-05 10:05:00+07'::timestamptz, '2026-01-05 10:05:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', 'a678ac27-3077-5ef2-8919-5218b2e48791', 'MEMBER', '2026-01-05 10:05:00+07'::timestamptz, 'bf434e4f-e1bf-5e50-93b0-8ee0bcd5d014', '2026-01-05 10:05:00+07'::timestamptz, '2026-01-05 10:05:00+07'::timestamptz);

-- ============================================================
-- 4. REQUIREMENTS
-- ============================================================
INSERT INTO public.requirements (project_id, type, title, description, priority, id, created_at, updated_at) VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'BUSINESS', 'Theo dõi hiệu quả vận hành kho lưu trữ hồ sơ bệnh án', 'Ban giám đốc bệnh viện cần nắm được tình hình lưu trữ hồ sơ bệnh án trên toàn viện: số lượng hồ sơ đang lưu trữ, tỷ lệ lấp đầy kho/tủ/ngăn, và tốc độ xử lý hồ sơ mượn/trả để lập kế hoạch mở rộng kho lưu trữ.', 'HIGH', '570cecdf-7f76-54ed-8375-c59446c6b4ec', '2025-11-05 09:30:00+07'::timestamptz, '2025-11-05 09:30:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'ANALYTICAL', 'Phân tích số lượng hồ sơ lưu trữ theo khoa và theo tháng', 'Cần thống kê số lượng hồ sơ bệnh án được đưa vào lưu trữ theo từng khoa (Vào từ khoa/Ra từ khoa) và theo từng tháng để phát hiện khoa nào phát sinh nhiều hồ sơ lưu trữ nhất.', 'HIGH', 'ef41f280-58cb-591e-b632-d91f33c11383', '2025-11-06 10:00:00+07'::timestamptz, '2025-11-06 10:00:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'ANALYTICAL', 'Phân tích tỷ lệ lấp đầy Kho - Tủ - Ngăn', 'Cần tính tỷ lệ lấp đầy (số hồ sơ / sức chứa) của từng Kho, từng Tủ và từng Ngăn để cảnh báo khi gần đầy, hỗ trợ điều phối vị trí lưu trữ mới.', 'MEDIUM', '8859e59b-6215-5416-ae06-8c8fd5e674a7', '2025-11-07 08:20:00+07'::timestamptz, '2025-11-07 08:20:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'TECHNICAL', 'Ẩn danh hóa dữ liệu định danh bệnh nhân trước khi đưa vào DW', 'Các trường như Họ và tên, Địa chỉ, Số bệnh án phải được ẩn danh hóa (hashing/masking) trước khi lưu vào các bảng fact/dimension công khai cho phân tích, chỉ giữ Số hồ sơ dạng mã hóa để truy vết khi cần.', 'HIGH', '9cc6179c-f4e3-5cb2-a4d0-a71f9c84511d', '2025-11-08 14:10:00+07'::timestamptz, '2025-11-08 14:10:00+07'::timestamptz),
  ('84bdeb46-0eba-564e-8437-833ede4e2718', 'ANALYTICAL', 'Phân tích lượt khám và chẩn đoán theo khoa/quý', 'Cần đo số lượt bệnh nhân vào viện, ra viện theo từng khoa và từng quý, kèm top 10 chẩn đoán phổ biến nhất để phục vụ báo cáo Sở Y tế.', 'HIGH', 'da3ce17b-dd03-5f74-af74-71ab701a72be', '2025-12-11 09:00:00+07'::timestamptz, '2025-12-11 09:00:00+07'::timestamptz),
  ('84bdeb46-0eba-564e-8437-833ede4e2718', 'ANALYTICAL', 'Phân tích cơ cấu đối tượng chi trả viện phí', 'Cần tính tỷ lệ bệnh nhân theo đối tượng chi trả (BHYT, BHYT Quân, Viện phí, Dịch vụ, Miễn phí) theo từng khoa và theo thời gian để đánh giá cơ cấu nguồn thu.', 'MEDIUM', 'f9711f5b-fd8f-54db-b376-16b19781095a', '2025-12-12 11:15:00+07'::timestamptz, '2025-12-12 11:15:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', 'ANALYTICAL', 'Phân tích giao dịch bất thường theo khách hàng và thời gian', 'Cần tổng hợp số lượng và giá trị giao dịch theo khách hàng, kênh giao dịch (ATM, Internet Banking, POS) theo từng ngày để phát hiện giao dịch bất thường vượt ngưỡng.', 'HIGH', '19feddd3-2507-545f-ae72-80cb52055602', '2025-11-09 09:00:00+07'::timestamptz, '2025-11-09 09:00:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', 'TECHNICAL', 'Mã hóa số tài khoản và CCCD khách hàng', 'Số tài khoản, số CCCD và số điện thoại khách hàng phải được mã hóa hai chiều (encryption at rest) và chỉ giải mã khi có thẩm quyền truy cập theo quy định bảo mật ngân hàng.', 'HIGH', '18ff1ee9-b7a0-5482-9b94-9716b7baea36', '2025-11-10 10:30:00+07'::timestamptz, '2025-11-10 10:30:00+07'::timestamptz),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d', 'ANALYTICAL', 'Phân tích doanh thu theo ngành hàng và khu vực', 'Cần tổng hợp doanh thu, số lượng đơn hàng theo ngành hàng, khu vực cửa hàng và theo tuần để xác định ngành hàng tăng trưởng/suy giảm.', 'HIGH', '5595825c-8ac4-5a53-abe1-0f4ca49e76f7', '2025-11-12 08:40:00+07'::timestamptz, '2025-11-12 08:40:00+07'::timestamptz),
  ('18525676-8c6b-552b-8de7-a50899ef4b92', 'ANALYTICAL', 'Phân tích tỷ lệ giao hàng đúng hạn theo tuyến', 'Cần đo tỷ lệ đơn hàng giao đúng hạn, thời gian trung chuyển trung bình theo từng tuyến vận chuyển và từng đối tác vận chuyển theo tháng.', 'HIGH', 'a4db5a66-b2ad-5171-91d5-401cb72e1bff', '2025-11-19 09:30:00+07'::timestamptz, '2025-11-19 09:30:00+07'::timestamptz),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277', 'ANALYTICAL', 'Phân tích tỷ lệ tốt nghiệp theo khoa/ngành', 'Cần thống kê số sinh viên nhập học, số sinh viên tốt nghiệp đúng hạn theo từng khoa/ngành và theo từng khóa học để đánh giá chất lượng đào tạo.', 'MEDIUM', '39163bc9-1fa4-5f99-9b25-68a2b7fff063', '2025-12-03 09:00:00+07'::timestamptz, '2025-12-03 09:00:00+07'::timestamptz),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48', 'ANALYTICAL', 'Phân tích chỉ số OEE theo dây chuyền sản xuất', 'Cần tính chỉ số OEE (Overall Equipment Effectiveness) theo từng dây chuyền, từng ca sản xuất, bao gồm tỷ lệ khả dụng, hiệu suất và chất lượng.', 'HIGH', 'fe5803e1-db15-5ba3-a81a-32e73a9be9da', '2025-12-09 08:15:00+07'::timestamptz, '2025-12-09 08:15:00+07'::timestamptz),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594', 'ANALYTICAL', 'Phân tích tỷ lệ bồi thường theo sản phẩm bảo hiểm', 'Cần tính tỷ lệ claim được duyệt/từ chối theo từng sản phẩm bảo hiểm và theo thời gian để đánh giá mức độ rủi ro của từng dòng sản phẩm.', 'MEDIUM', 'e33ff717-a4cb-5623-a2d1-a84c16a7d4cc', '2025-10-21 09:00:00+07'::timestamptz, '2025-10-21 09:00:00+07'::timestamptz),
  ('f8c4432f-0252-5275-a581-958039b98639', 'ANALYTICAL', 'Phân tích tỷ lệ rời mạng (churn) theo gói cước', 'Cần dự báo tỷ lệ thuê bao rời mạng theo từng gói cước, khu vực và theo tháng dựa trên lịch sử sử dụng lưu lượng và doanh thu ARPU.', 'HIGH', '056a6dd6-4c2d-57ca-83cc-cff6822d284d', '2025-12-16 10:00:00+07'::timestamptz, '2025-12-16 10:00:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', 'ANALYTICAL', 'Phân tích tỷ lệ bỏ giỏ hàng và hiệu quả kênh marketing', 'Cần đo tỷ lệ bỏ giỏ hàng theo từng danh mục sản phẩm, và hiệu quả chuyển đổi của từng kênh marketing (Facebook Ads, Google Ads, Email) theo tuần.', 'HIGH', '3ae76b93-52e4-5755-afe1-cae0085d4c97', '2026-01-06 09:30:00+07'::timestamptz, '2026-01-06 09:30:00+07'::timestamptz);

-- ============================================================
-- 5. ANALYTICAL_REQUIREMENTS
-- ============================================================
INSERT INTO public.analytical_requirements (requirement_id, metric, dimension, time_granularity, aggregation_method, grain, id, created_at, updated_at) VALUES
  ('ef41f280-58cb-591e-b632-d91f33c11383', 'Số lượng hồ sơ lưu trữ', 'Khoa (vào/ra)', 'Tháng', 'COUNT', 'Mỗi dòng = 1 hồ sơ lưu trữ, nhóm theo khoa và tháng lưu trữ', 'b0c6889c-f3f5-5bed-a0d3-13b3490c4767', '2025-11-06 10:00:00+07'::timestamptz, '2025-11-06 10:00:00+07'::timestamptz),
  ('8859e59b-6215-5416-ae06-8c8fd5e674a7', 'Tỷ lệ lấp đầy vị trí lưu trữ', 'Kho, Tủ, Ngăn', 'Ngày', 'AVG', 'Mỗi dòng = 1 vị trí lưu trữ (ngăn), tính theo số hồ sơ hiện có / sức chứa tại thời điểm snapshot theo ngày', '264ef9be-4fea-52bc-a117-99a6eb7f8f47', '2025-11-07 08:20:00+07'::timestamptz, '2025-11-07 08:20:00+07'::timestamptz),
  ('da3ce17b-dd03-5f74-af74-71ab701a72be', 'Số lượt khám bệnh', 'Khoa, Chẩn đoán', 'Quý', 'COUNT', 'Mỗi dòng = 1 lượt vào/ra viện của bệnh nhân, nhóm theo khoa và quý', 'ad73c3b5-3fec-5dca-b11d-d32a29c6e42c', '2025-12-11 09:00:00+07'::timestamptz, '2025-12-11 09:00:00+07'::timestamptz),
  ('f9711f5b-fd8f-54db-b376-16b19781095a', 'Số bệnh nhân theo đối tượng chi trả', 'Đối tượng chi trả, Khoa', 'Quý', 'COUNT', 'Mỗi dòng = 1 bệnh án, nhóm theo đối tượng chi trả và khoa', '90b35778-8996-555d-8e8f-6087150cece1', '2025-12-12 11:15:00+07'::timestamptz, '2025-12-12 11:15:00+07'::timestamptz),
  ('19feddd3-2507-545f-ae72-80cb52055602', 'Giá trị & số lượng giao dịch', 'Khách hàng, Kênh giao dịch', 'Ngày', 'SUM', 'Mỗi dòng = 1 giao dịch, nhóm theo khách hàng, kênh và ngày giao dịch', '087343bc-acb7-5ffb-8ebb-5e414c8d384a', '2025-11-09 09:00:00+07'::timestamptz, '2025-11-09 09:00:00+07'::timestamptz),
  ('5595825c-8ac4-5a53-abe1-0f4ca49e76f7', 'Doanh thu bán hàng', 'Ngành hàng, Khu vực', 'Tuần', 'SUM', 'Mỗi dòng = 1 dòng hóa đơn bán hàng (order line), nhóm theo ngành hàng, khu vực và tuần', 'e2733ad8-c03e-5157-a74c-3761efb09725', '2025-11-12 08:40:00+07'::timestamptz, '2025-11-12 08:40:00+07'::timestamptz),
  ('a4db5a66-b2ad-5171-91d5-401cb72e1bff', 'Tỷ lệ giao hàng đúng hạn', 'Tuyến vận chuyển, Đối tác', 'Tháng', 'AVG', 'Mỗi dòng = 1 vận đơn, nhóm theo tuyến vận chuyển, đối tác vận chuyển và tháng giao hàng', 'e2b336b4-29cf-5489-80df-d6cd31f0dd9a', '2025-11-19 09:30:00+07'::timestamptz, '2025-11-19 09:30:00+07'::timestamptz),
  ('39163bc9-1fa4-5f99-9b25-68a2b7fff063', 'Tỷ lệ tốt nghiệp', 'Khoa/Ngành, Khóa học', 'Năm học', 'AVG', 'Mỗi dòng = 1 sinh viên, nhóm theo khoa/ngành và khóa học nhập học', 'c46f00d2-dcfa-52c9-9b8d-164db566ee24', '2025-12-03 09:00:00+07'::timestamptz, '2025-12-03 09:00:00+07'::timestamptz),
  ('fe5803e1-db15-5ba3-a81a-32e73a9be9da', 'Chỉ số OEE', 'Dây chuyền, Ca sản xuất', 'Ca', 'AVG', 'Mỗi dòng = 1 ca sản xuất trên 1 dây chuyền, tính OEE = Availability x Performance x Quality', '346bc6a6-c524-5a2d-8e44-07f48f07fa1d', '2025-12-09 08:15:00+07'::timestamptz, '2025-12-09 08:15:00+07'::timestamptz),
  ('e33ff717-a4cb-5623-a2d1-a84c16a7d4cc', 'Tỷ lệ bồi thường', 'Sản phẩm bảo hiểm', 'Tháng', 'AVG', 'Mỗi dòng = 1 hồ sơ yêu cầu bồi thường (claim), nhóm theo sản phẩm bảo hiểm và tháng phát sinh', '156c0f5e-1958-5d67-a88a-a8c4d081fc0f', '2025-10-21 09:00:00+07'::timestamptz, '2025-10-21 09:00:00+07'::timestamptz),
  ('056a6dd6-4c2d-57ca-83cc-cff6822d284d', 'Tỷ lệ rời mạng', 'Gói cước, Khu vực', 'Tháng', 'AVG', 'Mỗi dòng = 1 thuê bao đang hoạt động, nhóm theo gói cước, khu vực và tháng quan sát', 'a0059bf6-b64d-580e-a847-313493ab2160', '2025-12-16 10:00:00+07'::timestamptz, '2025-12-16 10:00:00+07'::timestamptz),
  ('3ae76b93-52e4-5755-afe1-cae0085d4c97', 'Tỷ lệ bỏ giỏ hàng & hiệu quả marketing', 'Danh mục sản phẩm, Kênh marketing', 'Tuần', 'AVG', 'Mỗi dòng = 1 phiên mua sắm (session), nhóm theo danh mục sản phẩm, kênh marketing và tuần', '1a650908-3f52-5126-89e7-7ac7cd3475f8', '2026-01-06 09:30:00+07'::timestamptz, '2026-01-06 09:30:00+07'::timestamptz);
-- ============================================================
-- 6. DATA_SOURCES
-- ============================================================
INSERT INTO public.data_sources (project_id, name, type, description, location, schema_metadata, id, created_at, updated_at) VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'VIMES Patient Record - Hồ sơ lưu trữ (Export)', 'SQL', 'Bảng dữ liệu hồ sơ lưu trữ, thông tin bệnh nhân và danh sách bệnh nhân trích xuất từ hệ thống VIMES Patient Record qua kết nối SQL Server read-replica.', 'sqlserver://vimes-prod-replica.hospital.local:1433/VIMES_PatientRecord', '{"source_system": "VIMES Patient Record - Module Hồ sơ lưu trữ", "tables": [{"name": "ho_so_luu_tru", "description": "Hồ sơ bệnh án đã được lưu trữ vật lý (Sheet 3 - Thông tin hồ sơ lưu trữ)", "columns": [{"name": "so_benh_an", "data_type": "varchar(30)", "primary_key": true, "required": true, "note": "Định dạng NGTBD-nnn hoặc NOI-nnn, duy nhất theo đợt điều trị"}, {"name": "so_ho_so", "data_type": "integer", "required": true, "foreign_key": {"references": "danh_sach_benh_nhan.so_ho_so"}}, {"name": "thoi_gian_vao_vien", "data_type": "timestamp", "required": true, "note": "<= thời điểm hiện tại"}, {"name": "ngay_ra_vien", "data_type": "date", "required": false, "note": ">= thoi_gian_vao_vien nếu có"}, {"name": "khoa_vao_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "khoa_ra_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "chan_doan", "data_type": "varchar(250)", "required": false}, {"name": "so_luu_tru", "data_type": "integer", "primary_key": false, "required": true, "note": "Duy nhất trong phạm vi kho lưu trữ; chỉ chứa chữ số"}, {"name": "ngay_luu_tru", "data_type": "timestamp", "required": true, "note": ">= ngay_ra_vien"}, {"name": "trang_thai_ho_so_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_trang_thai_ho_so.ma"}}, {"name": "kho_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_kho.ma"}}, {"name": "tu_ma", "data_type": "varchar(20)", "required": true, "foreign_key": {"references": "dm_tu.ma"}}, {"name": "ngan_ma", "data_type": "varchar(20)", "required": true, "foreign_key": {"references": "dm_ngan.ma"}}, {"name": "vi_tri", "data_type": "varchar(50)", "required": false, "note": "VD: Kệ 2 - Hàng 5"}, {"name": "ky_hieu", "data_type": "varchar(20)", "required": false, "note": "Tối đa 20 ký tự, chữ/số viết tắt"}, {"name": "ghi_chu", "data_type": "varchar(500)", "required": false}], "sample_rows": [{"so_benh_an": "NOI-300", "so_ho_so": 15020001, "thoi_gian_vao_vien": "2015-01-18 16:00:00", "ngay_ra_vien": "2015-02-06", "khoa_vao_ma": "A7", "khoa_ra_ma": "A7", "chan_doan": "Nhồi máu cơ tim cấp", "so_luu_tru": 1, "ngay_luu_tru": "2015-02-07 16:00:00", "trang_thai_ho_so_ma": "CDH", "kho_ma": "K2", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-1", "vi_tri": "Kệ 1 - Hàng 4", "ky_hieu": "A7-15020001", "ghi_chu": null}, {"so_benh_an": "NGTBD-301", "so_ho_so": 15020002, "thoi_gian_vao_vien": "2015-02-27 09:00:00", "ngay_ra_vien": "2015-03-15", "khoa_vao_ma": "B9", "khoa_ra_ma": "B9", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng", "so_luu_tru": 2, "ngay_luu_tru": "2015-03-20 09:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K1", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-2", "vi_tri": "Kệ 3 - Hàng 5", "ky_hieu": "B9-15020002", "ghi_chu": null}, {"so_benh_an": "NOI-302", "so_ho_so": 15020003, "thoi_gian_vao_vien": "2015-02-07 18:00:00", "ngay_ra_vien": "2015-02-10", "khoa_vao_ma": "A2", "khoa_ra_ma": "A2", "chan_doan": "Sỏi thận", "so_luu_tru": 3, "ngay_luu_tru": "2015-02-14 18:00:00", "trang_thai_ho_so_ma": "CDH", "kho_ma": "K1", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-1", "vi_tri": "Kệ 3 - Hàng 6", "ky_hieu": "A2-15020003", "ghi_chu": null}, {"so_benh_an": "NOI-303", "so_ho_so": 15020004, "thoi_gian_vao_vien": "2015-02-22 10:00:00", "ngay_ra_vien": "2015-03-10", "khoa_vao_ma": "A2", "khoa_ra_ma": "KB", "chan_doan": "Đái tháo đường type 2", "so_luu_tru": 4, "ngay_luu_tru": "2015-03-13 10:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K2", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-2", "vi_tri": "Kệ 3 - Hàng 2", "ky_hieu": "A2-15020004", "ghi_chu": "Hồ sơ cần bổ sung xét nghiệm"}, {"so_benh_an": "NOI-304", "so_ho_so": 15020005, "thoi_gian_vao_vien": "2015-02-02 16:00:00", "ngay_ra_vien": "2015-02-14", "khoa_vao_ma": "A16", "khoa_ra_ma": "A16", "chan_doan": "Viêm xoang mạn tính", "so_luu_tru": 5, "ngay_luu_tru": "2015-02-15 16:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K1", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-3", "vi_tri": "Kệ 3 - Hàng 2", "ky_hieu": "A16-15020005", "ghi_chu": null}, {"so_benh_an": "NOI-305", "so_ho_so": 15020006, "thoi_gian_vao_vien": "2015-01-23 10:00:00", "ngay_ra_vien": "2015-01-29", "khoa_vao_ma": "A16", "khoa_ra_ma": "B6", "chan_doan": "U xơ tử cung", "so_luu_tru": 6, "ngay_luu_tru": "2015-01-31 10:00:00", "trang_thai_ho_so_ma": "CDH", "kho_ma": "K3", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-1", "vi_tri": "Kệ 4 - Hàng 7", "ky_hieu": "A16-15020006", "ghi_chu": null}, {"so_benh_an": "NGTBD-306", "so_ho_so": 15020007, "thoi_gian_vao_vien": "2015-01-25 18:00:00", "ngay_ra_vien": "2015-02-09", "khoa_vao_ma": "KB", "khoa_ra_ma": "KB", "chan_doan": "Viêm xoang mạn tính", "so_luu_tru": 7, "ngay_luu_tru": "2015-02-14 18:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K2", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-2", "vi_tri": "Kệ 4 - Hàng 5", "ky_hieu": "KB-15020007", "ghi_chu": "Hồ sơ cần bổ sung xét nghiệm"}, {"so_benh_an": "NOI-307", "so_ho_so": 15020008, "thoi_gian_vao_vien": "2015-02-11 12:00:00", "ngay_ra_vien": "2015-02-18", "khoa_vao_ma": "XT", "khoa_ra_ma": "XT", "chan_doan": "Đái tháo đường type 2", "so_luu_tru": 8, "ngay_luu_tru": "2015-02-22 12:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K3", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-3", "vi_tri": "Kệ 2 - Hàng 2", "ky_hieu": "XT-15020008", "ghi_chu": "Hồ sơ cần bổ sung xét nghiệm"}, {"so_benh_an": "NOI-308", "so_ho_so": 15020009, "thoi_gian_vao_vien": "2015-01-05 15:00:00", "ngay_ra_vien": "2015-01-17", "khoa_vao_ma": "XT", "khoa_ra_ma": "XT", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng", "so_luu_tru": 9, "ngay_luu_tru": "2015-01-21 15:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K1", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-3", "vi_tri": "Kệ 2 - Hàng 1", "ky_hieu": "XT-15020009", "ghi_chu": null}, {"so_benh_an": "NOI-309", "so_ho_so": 15020010, "thoi_gian_vao_vien": "2015-01-21 08:00:00", "ngay_ra_vien": "2015-02-07", "khoa_vao_ma": "KB", "khoa_ra_ma": "KB", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng", "so_luu_tru": 10, "ngay_luu_tru": "2015-02-12 08:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K2", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-1", "vi_tri": "Kệ 4 - Hàng 4", "ky_hieu": "KB-15020010", "ghi_chu": "Hồ sơ cần bổ sung xét nghiệm"}, {"so_benh_an": "NOI-310", "so_ho_so": 15020011, "thoi_gian_vao_vien": "2015-02-05 09:00:00", "ngay_ra_vien": "2015-02-09", "khoa_vao_ma": "B1-A", "khoa_ra_ma": "B1-A", "chan_doan": "Đái tháo đường type 2", "so_luu_tru": 11, "ngay_luu_tru": "2015-02-12 09:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K3", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-1", "vi_tri": "Kệ 2 - Hàng 1", "ky_hieu": "B1-A-15020011", "ghi_chu": null}, {"so_benh_an": "NGTBD-311", "so_ho_so": 15020012, "thoi_gian_vao_vien": "2015-02-04 10:00:00", "ngay_ra_vien": "2015-02-21", "khoa_vao_ma": "A1", "khoa_ra_ma": "A2", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng", "so_luu_tru": 12, "ngay_luu_tru": "2015-02-23 10:00:00", "trang_thai_ho_so_ma": "CDH", "kho_ma": "K1", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-2", "vi_tri": "Kệ 4 - Hàng 4", "ky_hieu": "A1-15020012", "ghi_chu": "Hồ sơ cần bổ sung xét nghiệm"}, {"so_benh_an": "NOI-312", "so_ho_so": 15020013, "thoi_gian_vao_vien": "2015-03-01 03:20:00", "ngay_ra_vien": "2015-03-05", "khoa_vao_ma": "A15", "khoa_ra_ma": "A15", "chan_doan": "Theo dõi sau sinh", "so_luu_tru": 13, "ngay_luu_tru": "2015-03-08 09:00:00", "trang_thai_ho_so_ma": "DM", "kho_ma": "K1", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-3", "vi_tri": "Kệ 1 - Hàng 1", "ky_hieu": "A15-15020013", "ghi_chu": "Hồ sơ đang được Phòng KHTH mượn để nghiên cứu"}, {"so_benh_an": "NGTBD-313", "so_ho_so": 15020014, "thoi_gian_vao_vien": "2015-03-02 07:30:00", "ngay_ra_vien": "2015-03-02", "khoa_vao_ma": "A1", "khoa_ra_ma": "A1", "chan_doan": "Tăng huyết áp", "so_luu_tru": 14, "ngay_luu_tru": "2015-03-04 10:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K3", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-2", "vi_tri": "Kệ 1 - Hàng 3", "ky_hieu": "A1-15020014", "ghi_chu": null}, {"so_benh_an": "NOI-314", "so_ho_so": 15020015, "thoi_gian_vao_vien": "2015-03-03 14:00:00", "ngay_ra_vien": "2015-03-06", "khoa_vao_ma": "B3", "khoa_ra_ma": "B3", "chan_doan": null, "so_luu_tru": 15, "ngay_luu_tru": "2015-03-09 10:00:00", "trang_thai_ho_so_ma": "DH", "kho_ma": "K1", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-1", "vi_tri": null, "ky_hieu": "B3-15020015", "ghi_chu": "Hồ sơ trùng lặp, đã hủy theo quyết định số 12/QĐ-KHTH"}, {"so_benh_an": "NOI-315", "so_ho_so": 15020016, "thoi_gian_vao_vien": "2015-03-04 09:00:00", "ngay_ra_vien": "2015-03-08", "khoa_vao_ma": "A8", "khoa_ra_ma": "A8", "chan_doan": null, "so_luu_tru": 16, "ngay_luu_tru": "2015-03-11 09:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K2", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-3", "vi_tri": "Kệ 1 - Hàng 2", "ky_hieu": "A8-15020016", "ghi_chu": null}, {"so_benh_an": "NGTBD-316", "so_ho_so": 15020017, "thoi_gian_vao_vien": "2015-03-05 08:00:00", "ngay_ra_vien": "2015-03-05", "khoa_vao_ma": "KB", "khoa_ra_ma": "KB", "chan_doan": "Khám sức khỏe định kỳ", "so_luu_tru": 17, "ngay_luu_tru": "2015-03-06 10:00:00", "trang_thai_ho_so_ma": "DLT", "kho_ma": "K2", "tu_ma": "T-K1-A", "ngan_ma": "N-TA-1", "vi_tri": "Kệ 1 - Hàng 2", "ky_hieu": "KB-15020017", "ghi_chu": null}, {"so_benh_an": "NOI-317", "so_ho_so": 15020018, "thoi_gian_vao_vien": "2015-03-06 20:00:00", "ngay_ra_vien": "2015-03-20", "khoa_vao_ma": "B6", "khoa_ra_ma": "B1-C", "chan_doan": "Gãy xương đùi", "so_luu_tru": 18, "ngay_luu_tru": "2015-03-23 10:00:00", "trang_thai_ho_so_ma": "CDH", "kho_ma": "K3", "tu_ma": "T-K1-B", "ngan_ma": "N-TA-2", "vi_tri": "Kệ 3 - Hàng 3", "ky_hieu": "B1C-15020018", "ghi_chu": null}]}, {"name": "thong_tin_benh_nhan", "description": "Thông tin hành chính bệnh nhân gắn với bệnh án (Sheet 2)", "columns": [{"name": "so_ho_so", "data_type": "integer", "primary_key": true, "required": true, "note": "Tự sinh hoặc nhập tay, không trùng lặp"}, {"name": "so_benh_an", "data_type": "varchar(30)", "required": true, "foreign_key": {"references": "ho_so_luu_tru.so_benh_an"}}, {"name": "ho_ten", "data_type": "varchar(100)", "required": true, "pii": true, "note": "Tối đa 100 ký tự, không chứa số"}, {"name": "tuoi", "data_type": "integer", "required": true, "note": "Giá trị nguyên dương, trong khoảng 0-130"}, {"name": "gioi_tinh_ma", "data_type": "varchar(2)", "required": true, "foreign_key": {"references": "dm_gioi_tinh.ma"}}, {"name": "dia_chi", "data_type": "varchar(250)", "required": false, "pii": true}, {"name": "nghe_nghiep", "data_type": "varchar(100)", "required": false, "foreign_key": {"references": "dm_nghe_nghiep.ma", "nullable": true}, "note": "Có thể chọn từ danh mục dm_nghe_nghiep hoặc nhập văn bản tự do"}, {"name": "doi_tuong_ma", "data_type": "varchar(20)", "required": true, "foreign_key": {"references": "dm_doi_tuong.ma"}}, {"name": "loai_benh_an_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_loai_benh_an.ma"}}], "sample_rows": [{"so_ho_so": 15020001, "so_benh_an": "NOI-300", "ho_ten": "Nguyễn Văn An", "tuoi": 87, "gioi_tinh_ma": "1", "dia_chi": "Phường Nghĩa Tân, Quận Cầu Giấy, TP Hà Nội", "nghe_nghiep": "CNVC", "doi_tuong_ma": "BHYT", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020002, "so_benh_an": "NGTBD-301", "ho_ten": "Trần Thị Bình", "tuoi": 83, "gioi_tinh_ma": "2", "dia_chi": "Phường Thanh Xuân Bắc, Quận Thanh Xuân, TP Hà Nội", "nghe_nghiep": "BD", "doi_tuong_ma": "MP", "loai_benh_an_ma": "NGT"}, {"so_ho_so": 15020003, "so_benh_an": "NOI-302", "ho_ten": "Lê Văn Cường", "tuoi": 49, "gioi_tinh_ma": "1", "dia_chi": "Xã Đông Dư, Huyện Gia Lâm, TP Hà Nội", "nghe_nghiep": "CNVC", "doi_tuong_ma": "BHYT", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020004, "so_benh_an": "NOI-303", "ho_ten": "Phạm Thị Dung", "tuoi": 14, "gioi_tinh_ma": "2", "dia_chi": "Phường Xuân Đỉnh, Quận Bắc Từ Liêm, TP Hà Nội", "nghe_nghiep": "BD", "doi_tuong_ma": "BHYT_QUAN", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020005, "so_benh_an": "NOI-304", "ho_ten": "Hoàng Văn Em", "tuoi": 27, "gioi_tinh_ma": "1", "dia_chi": "Thị trấn Trâu Quỳ, Huyện Gia Lâm, TP Hà Nội", "nghe_nghiep": "ND", "doi_tuong_ma": "BHYT_QUAN", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020006, "so_benh_an": "NOI-305", "ho_ten": "Vũ Thị Phương", "tuoi": 78, "gioi_tinh_ma": "2", "dia_chi": "Phường Ngọc Lâm, Quận Long Biên, TP Hà Nội", "nghe_nghiep": "HT", "doi_tuong_ma": "BHYT_QUAN", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020007, "so_benh_an": "NGTBD-306", "ho_ten": "Đặng Văn Giang", "tuoi": 23, "gioi_tinh_ma": "1", "dia_chi": "Xã Vân Canh, Huyện Hoài Đức, TP Hà Nội", "nghe_nghiep": "K", "doi_tuong_ma": "BHYT", "loai_benh_an_ma": "NGT"}, {"so_ho_so": 15020008, "so_benh_an": "NOI-307", "ho_ten": "Bùi Thị Hoa", "tuoi": 7, "gioi_tinh_ma": "2", "dia_chi": "Phường Dịch Vọng, Quận Cầu Giấy, TP Hà Nội", "nghe_nghiep": "CNVC", "doi_tuong_ma": "MP", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020009, "so_benh_an": "NOI-308", "ho_ten": "Đỗ Văn Inh", "tuoi": 44, "gioi_tinh_ma": "1", "dia_chi": "Phường Mai Dịch, Quận Cầu Giấy, TP Hà Nội", "nghe_nghiep": "ND", "doi_tuong_ma": "BHYT_QUAN", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020010, "so_benh_an": "NOI-309", "ho_ten": "Ngô Thị Kim", "tuoi": 78, "gioi_tinh_ma": "2", "dia_chi": "Xã Kim Chung, Huyện Đông Anh, TP Hà Nội", "nghe_nghiep": "CNVC", "doi_tuong_ma": "BHYT", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020011, "so_benh_an": "NOI-310", "ho_ten": "Dương Văn Long", "tuoi": 31, "gioi_tinh_ma": "1", "dia_chi": "Phường Yên Hòa, Quận Cầu Giấy, TP Hà Nội", "nghe_nghiep": "HSSV", "doi_tuong_ma": "DV", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020012, "so_benh_an": "NGTBD-311", "ho_ten": "Đinh Thị Mai", "tuoi": 86, "gioi_tinh_ma": "2", "dia_chi": "Phường Trung Hòa, Quận Cầu Giấy, TP Hà Nội", "nghe_nghiep": "BD", "doi_tuong_ma": "BHYT_QUAN", "loai_benh_an_ma": "NGT"}, {"so_ho_so": 15020013, "so_benh_an": "NOI-312", "ho_ten": "Bùi Sơ Sinh Nam", "tuoi": 0, "gioi_tinh_ma": "1", "dia_chi": "Phường Thịnh Liệt, Quận Hoàng Mai, TP Hà Nội", "nghe_nghiep": null, "doi_tuong_ma": "MP", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020014, "so_benh_an": "NGTBD-313", "ho_ten": "Trịnh Văn Thọ", "tuoi": 130, "gioi_tinh_ma": "1", "dia_chi": "Phường Nghĩa Đô, Quận Cầu Giấy, TP Hà Nội", "nghe_nghiep": "HT", "doi_tuong_ma": "BHYT", "loai_benh_an_ma": "NGT"}, {"so_ho_so": 15020015, "so_benh_an": "NOI-314", "ho_ten": "Lý Thị Xuân", "tuoi": 45, "gioi_tinh_ma": "2", "dia_chi": "Phường Ngã Tư Sở, Quận Đống Đa, TP Hà Nội", "nghe_nghiep": "Giáo viên mầm non", "doi_tuong_ma": "VP", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020016, "so_benh_an": "NOI-315", "ho_ten": "Nguyễn Văn Bảo Long", "tuoi": 5, "gioi_tinh_ma": "1", "dia_chi": "Phường Cống Vị, Quận Ba Đình, TP Hà Nội", "nghe_nghiep": null, "doi_tuong_ma": "DV", "loai_benh_an_ma": "NOI"}, {"so_ho_so": 15020017, "so_benh_an": "NGTBD-316", "ho_ten": "Phan Thị Cẩm", "tuoi": 62, "gioi_tinh_ma": "2", "dia_chi": "Phường Trung Liệt, Quận Đống Đa, TP Hà Nội", "nghe_nghiep": "TD", "doi_tuong_ma": "BHYT_QUAN", "loai_benh_an_ma": "NGT"}, {"so_ho_so": 15020018, "so_benh_an": "NOI-317", "ho_ten": "Đào Văn Đạt", "tuoi": 33, "gioi_tinh_ma": "1", "dia_chi": null, "nghe_nghiep": "TD", "doi_tuong_ma": "MP", "loai_benh_an_ma": "NOI"}]}, {"name": "danh_sach_benh_nhan", "description": "Danh sách tổng hợp toàn bộ bệnh nhân đã lưu trữ hồ sơ (Sheet 4 - dùng cho grid tổng hợp/báo cáo)", "columns": [{"name": "so_ho_so", "data_type": "integer", "primary_key": true, "required": true}, {"name": "so_luu_tru", "data_type": "integer", "required": true}, {"name": "ten_benh_nhan", "data_type": "varchar(100)", "required": true, "pii": true, "note": "Tối đa 100 ký tự, không chứa số"}, {"name": "tuoi", "data_type": "integer", "required": true, "note": "Giá trị nguyên dương, trong khoảng 0-130"}, {"name": "gioi_tinh_ma", "data_type": "varchar(2)", "required": true, "foreign_key": {"references": "dm_gioi_tinh.ma"}}, {"name": "dia_chi", "data_type": "varchar(250)", "required": false, "pii": true}, {"name": "thoi_gian_vao_vien", "data_type": "date", "required": true}, {"name": "ngay_ra", "data_type": "date", "required": false}, {"name": "khoa_vao_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "khoa_ra_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "chan_doan", "data_type": "varchar(250)", "required": false}], "sample_rows": [{"so_ho_so": 15020001, "so_luu_tru": 1, "ten_benh_nhan": "Nguyễn Văn An", "tuoi": 87, "gioi_tinh_ma": "1", "dia_chi": "Phường Nghĩa Tân, Quận Cầu Giấy, TP Hà Nội", "thoi_gian_vao_vien": "2015-01-18 16:00:00", "ngay_ra": "2015-02-06", "khoa_vao_ma": "A7", "khoa_ra_ma": "A7", "chan_doan": "Nhồi máu cơ tim cấp"}, {"so_ho_so": 15020002, "so_luu_tru": 2, "ten_benh_nhan": "Trần Thị Bình", "tuoi": 83, "gioi_tinh_ma": "2", "dia_chi": "Phường Thanh Xuân Bắc, Quận Thanh Xuân, TP Hà Nội", "thoi_gian_vao_vien": "2015-02-27 09:00:00", "ngay_ra": "2015-03-15", "khoa_vao_ma": "B9", "khoa_ra_ma": "B9", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng"}, {"so_ho_so": 15020003, "so_luu_tru": 3, "ten_benh_nhan": "Lê Văn Cường", "tuoi": 49, "gioi_tinh_ma": "1", "dia_chi": "Xã Đông Dư, Huyện Gia Lâm, TP Hà Nội", "thoi_gian_vao_vien": "2015-02-07 18:00:00", "ngay_ra": "2015-02-10", "khoa_vao_ma": "A2", "khoa_ra_ma": "A2", "chan_doan": "Sỏi thận"}, {"so_ho_so": 15020004, "so_luu_tru": 4, "ten_benh_nhan": "Phạm Thị Dung", "tuoi": 14, "gioi_tinh_ma": "2", "dia_chi": "Phường Xuân Đỉnh, Quận Bắc Từ Liêm, TP Hà Nội", "thoi_gian_vao_vien": "2015-02-22 10:00:00", "ngay_ra": "2015-03-10", "khoa_vao_ma": "A2", "khoa_ra_ma": "KB", "chan_doan": "Đái tháo đường type 2"}, {"so_ho_so": 15020005, "so_luu_tru": 5, "ten_benh_nhan": "Hoàng Văn Em", "tuoi": 27, "gioi_tinh_ma": "1", "dia_chi": "Thị trấn Trâu Quỳ, Huyện Gia Lâm, TP Hà Nội", "thoi_gian_vao_vien": "2015-02-02 16:00:00", "ngay_ra": "2015-02-14", "khoa_vao_ma": "A16", "khoa_ra_ma": "A16", "chan_doan": "Viêm xoang mạn tính"}, {"so_ho_so": 15020006, "so_luu_tru": 6, "ten_benh_nhan": "Vũ Thị Phương", "tuoi": 78, "gioi_tinh_ma": "2", "dia_chi": "Phường Ngọc Lâm, Quận Long Biên, TP Hà Nội", "thoi_gian_vao_vien": "2015-01-23 10:00:00", "ngay_ra": "2015-01-29", "khoa_vao_ma": "A16", "khoa_ra_ma": "B6", "chan_doan": "U xơ tử cung"}, {"so_ho_so": 15020007, "so_luu_tru": 7, "ten_benh_nhan": "Đặng Văn Giang", "tuoi": 23, "gioi_tinh_ma": "1", "dia_chi": "Xã Vân Canh, Huyện Hoài Đức, TP Hà Nội", "thoi_gian_vao_vien": "2015-01-25 18:00:00", "ngay_ra": "2015-02-09", "khoa_vao_ma": "KB", "khoa_ra_ma": "KB", "chan_doan": "Viêm xoang mạn tính"}, {"so_ho_so": 15020008, "so_luu_tru": 8, "ten_benh_nhan": "Bùi Thị Hoa", "tuoi": 7, "gioi_tinh_ma": "2", "dia_chi": "Phường Dịch Vọng, Quận Cầu Giấy, TP Hà Nội", "thoi_gian_vao_vien": "2015-02-11 12:00:00", "ngay_ra": "2015-02-18", "khoa_vao_ma": "XT", "khoa_ra_ma": "XT", "chan_doan": "Đái tháo đường type 2"}, {"so_ho_so": 15020009, "so_luu_tru": 9, "ten_benh_nhan": "Đỗ Văn Inh", "tuoi": 44, "gioi_tinh_ma": "1", "dia_chi": "Phường Mai Dịch, Quận Cầu Giấy, TP Hà Nội", "thoi_gian_vao_vien": "2015-01-05 15:00:00", "ngay_ra": "2015-01-17", "khoa_vao_ma": "XT", "khoa_ra_ma": "XT", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng"}, {"so_ho_so": 15020010, "so_luu_tru": 10, "ten_benh_nhan": "Ngô Thị Kim", "tuoi": 78, "gioi_tinh_ma": "2", "dia_chi": "Xã Kim Chung, Huyện Đông Anh, TP Hà Nội", "thoi_gian_vao_vien": "2015-01-21 08:00:00", "ngay_ra": "2015-02-07", "khoa_vao_ma": "KB", "khoa_ra_ma": "KB", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng"}, {"so_ho_so": 15020011, "so_luu_tru": 11, "ten_benh_nhan": "Dương Văn Long", "tuoi": 31, "gioi_tinh_ma": "1", "dia_chi": "Phường Yên Hòa, Quận Cầu Giấy, TP Hà Nội", "thoi_gian_vao_vien": "2015-02-05 09:00:00", "ngay_ra": "2015-02-09", "khoa_vao_ma": "B1-A", "khoa_ra_ma": "B1-A", "chan_doan": "Đái tháo đường type 2"}, {"so_ho_so": 15020012, "so_luu_tru": 12, "ten_benh_nhan": "Đinh Thị Mai", "tuoi": 86, "gioi_tinh_ma": "2", "dia_chi": "Phường Trung Hòa, Quận Cầu Giấy, TP Hà Nội", "thoi_gian_vao_vien": "2015-02-04 10:00:00", "ngay_ra": "2015-02-21", "khoa_vao_ma": "A1", "khoa_ra_ma": "A2", "chan_doan": "Thoát vị đĩa đệm cột sống thắt lưng"}, {"so_ho_so": 15020013, "so_luu_tru": 13, "ten_benh_nhan": "Bùi Sơ Sinh Nam", "tuoi": 0, "gioi_tinh_ma": "1", "dia_chi": "Phường Thịnh Liệt, Quận Hoàng Mai, TP Hà Nội", "thoi_gian_vao_vien": "2015-03-01 03:20:00", "ngay_ra": "2015-03-05", "khoa_vao_ma": "A15", "khoa_ra_ma": "A15", "chan_doan": "Theo dõi sau sinh"}, {"so_ho_so": 15020014, "so_luu_tru": 14, "ten_benh_nhan": "Trịnh Văn Thọ", "tuoi": 130, "gioi_tinh_ma": "1", "dia_chi": "Phường Nghĩa Đô, Quận Cầu Giấy, TP Hà Nội", "thoi_gian_vao_vien": "2015-03-02 07:30:00", "ngay_ra": "2015-03-02", "khoa_vao_ma": "A1", "khoa_ra_ma": "A1", "chan_doan": "Tăng huyết áp"}, {"so_ho_so": 15020015, "so_luu_tru": 15, "ten_benh_nhan": "Lý Thị Xuân", "tuoi": 45, "gioi_tinh_ma": "2", "dia_chi": "Phường Ngã Tư Sở, Quận Đống Đa, TP Hà Nội", "thoi_gian_vao_vien": "2015-03-03 14:00:00", "ngay_ra": "2015-03-06", "khoa_vao_ma": "B3", "khoa_ra_ma": "B3", "chan_doan": null}, {"so_ho_so": 15020016, "so_luu_tru": 16, "ten_benh_nhan": "Nguyễn Văn Bảo Long", "tuoi": 5, "gioi_tinh_ma": "1", "dia_chi": "Phường Cống Vị, Quận Ba Đình, TP Hà Nội", "thoi_gian_vao_vien": "2015-03-04 09:00:00", "ngay_ra": "2015-03-08", "khoa_vao_ma": "A8", "khoa_ra_ma": "A8", "chan_doan": null}, {"so_ho_so": 15020017, "so_luu_tru": 17, "ten_benh_nhan": "Phan Thị Cẩm", "tuoi": 62, "gioi_tinh_ma": "2", "dia_chi": "Phường Trung Liệt, Quận Đống Đa, TP Hà Nội", "thoi_gian_vao_vien": "2015-03-05 08:00:00", "ngay_ra": "2015-03-05", "khoa_vao_ma": "KB", "khoa_ra_ma": "KB", "chan_doan": "Khám sức khỏe định kỳ"}, {"so_ho_so": 15020018, "so_luu_tru": 18, "ten_benh_nhan": "Đào Văn Đạt", "tuoi": 33, "gioi_tinh_ma": "1", "dia_chi": null, "thoi_gian_vao_vien": "2015-03-06 20:00:00", "ngay_ra": "2015-03-20", "khoa_vao_ma": "B6", "khoa_ra_ma": "B1-C", "chan_doan": "Gãy xương đùi"}]}, {"name": "dm_gioi_tinh", "description": "Danh mục giới tính", "columns": [{"name": "ma", "data_type": "varchar(2)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(20)"}], "sample_rows": [{"ma": "1", "ten_hien_thi": "Nam"}, {"ma": "2", "ten_hien_thi": "Nữ"}]}, {"name": "dm_khoa", "description": "Danh mục khoa/phòng bệnh viện", "columns": [{"name": "ma_khoa", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_khoa", "data_type": "varchar(100)"}], "sample_rows": [{"ma_khoa": "A1", "ten_khoa": "Khoa A1 - Nội tổng hợp"}, {"ma_khoa": "A2", "ten_khoa": "Khoa A2 - Chấn thương chỉnh hình"}, {"ma_khoa": "A6", "ten_khoa": "Khoa A6 - Huyết học lâm sàng"}, {"ma_khoa": "A7", "ten_khoa": "Khoa A7 - Nội thận - Tiết niệu"}, {"ma_khoa": "A8", "ten_khoa": "Khoa A8 - Da liễu"}, {"ma_khoa": "A15", "ten_khoa": "Khoa A15 - Nội tổng hợp"}, {"ma_khoa": "A16", "ten_khoa": "Khoa A16 - Quốc tế"}, {"ma_khoa": "B1-A", "ten_khoa": "Khoa B1-A - Chẩn đoán hình ảnh (CT-Can thiệp)"}, {"ma_khoa": "B1-C", "ten_khoa": "Khoa B1-C - Phẫu thuật"}, {"ma_khoa": "B3", "ten_khoa": "Khoa B3 - Ngoại tổng hợp"}, {"ma_khoa": "B6", "ten_khoa": "Khoa B6 - Ngoại chấn thương"}, {"ma_khoa": "B9", "ten_khoa": "Khoa B9 - Tai - Mũi - Họng"}, {"ma_khoa": "XT", "ten_khoa": "Khoa Xạ trị"}, {"ma_khoa": "KB", "ten_khoa": "Khoa Khám bệnh"}]}, {"name": "dm_doi_tuong", "description": "Danh mục đối tượng chi trả viện phí", "columns": [{"name": "ma", "data_type": "varchar(20)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "BHYT", "ten_hien_thi": "BHYT"}, {"ma": "BHYT_QUAN", "ten_hien_thi": "BHYT Quân"}, {"ma": "VP", "ten_hien_thi": "Viện phí (Tự trả)"}, {"ma": "DV", "ten_hien_thi": "Dịch vụ"}, {"ma": "MP", "ten_hien_thi": "Miễn phí"}]}, {"name": "dm_loai_benh_an", "description": "Danh mục loại bệnh án", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(100)"}], "sample_rows": [{"ma": "NGT", "ten_hien_thi": "Bệnh án điều trị ngoại trú"}, {"ma": "NOI", "ten_hien_thi": "Bệnh án điều trị nội trú"}]}, {"name": "dm_trang_thai_ho_so", "description": "Danh mục trạng thái hồ sơ lưu trữ", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "DLT", "ten_hien_thi": "Hồ sơ đang lưu trữ"}, {"ma": "DM", "ten_hien_thi": "Hồ sơ đang mượn"}, {"ma": "CDH", "ten_hien_thi": "Hồ sơ chờ đưa vào kho"}, {"ma": "DH", "ten_hien_thi": "Hồ sơ đã hủy"}]}, {"name": "dm_kho", "description": "Danh mục kho lưu trữ", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "K1", "ten_hien_thi": "Kho 1"}, {"ma": "K2", "ten_hien_thi": "Kho 2"}, {"ma": "K3", "ten_hien_thi": "Kho 3"}]}, {"name": "dm_tu", "description": "Danh mục tủ lưu trữ (thuộc 1 kho)", "columns": [{"name": "ma", "data_type": "varchar(20)", "primary_key": true}, {"name": "kho_ma", "data_type": "varchar(10)", "foreign_key": {"references": "dm_kho.ma"}}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "T-K1-A", "ten_hien_thi": "Tủ A (thuộc Kho 1)"}, {"ma": "T-K1-B", "ten_hien_thi": "Tủ B (thuộc Kho 1)"}, {"ma": "T-K2-A", "ten_hien_thi": "Tủ A (thuộc Kho 2)"}]}, {"name": "dm_ngan", "description": "Danh mục ngăn lưu trữ (thuộc 1 tủ)", "columns": [{"name": "ma", "data_type": "varchar(20)", "primary_key": true}, {"name": "tu_ma", "data_type": "varchar(20)", "foreign_key": {"references": "dm_tu.ma"}}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "N-TA-1", "ten_hien_thi": "Ngăn 1 (thuộc Tủ A)"}, {"ma": "N-TA-2", "ten_hien_thi": "Ngăn 2 (thuộc Tủ A)"}, {"ma": "N-TA-3", "ten_hien_thi": "Ngăn 3 (thuộc Tủ A)"}]}, {"name": "dm_nghe_nghiep", "description": "Danh mục nghề nghiệp (tùy chọn, có thể để dạng Text tự do)", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "BD", "ten_hien_thi": "Bộ đội"}, {"ma": "CNVC", "ten_hien_thi": "Cán bộ - công chức - viên chức"}, {"ma": "CN", "ten_hien_thi": "Công nhân"}, {"ma": "ND", "ten_hien_thi": "Nông dân"}, {"ma": "HSSV", "ten_hien_thi": "Học sinh - Sinh viên"}, {"ma": "HT", "ten_hien_thi": "Hưu trí"}, {"ma": "TD", "ten_hien_thi": "Tự do"}, {"ma": "K", "ten_hien_thi": "Khác"}]}], "relationships": [{"from": "ho_so_luu_tru.so_ho_so", "to": "danh_sach_benh_nhan.so_ho_so", "type": "many_to_one"}, {"from": "thong_tin_benh_nhan.so_benh_an", "to": "ho_so_luu_tru.so_benh_an", "type": "one_to_one"}, {"from": "ho_so_luu_tru.khoa_vao_ma", "to": "dm_khoa.ma_khoa", "type": "many_to_one"}, {"from": "ho_so_luu_tru.khoa_ra_ma", "to": "dm_khoa.ma_khoa", "type": "many_to_one"}, {"from": "ho_so_luu_tru.kho_ma", "to": "dm_kho.ma", "type": "many_to_one"}, {"from": "ho_so_luu_tru.tu_ma", "to": "dm_tu.ma", "type": "many_to_one"}, {"from": "ho_so_luu_tru.ngan_ma", "to": "dm_ngan.ma", "type": "many_to_one"}, {"from": "dm_tu.kho_ma", "to": "dm_kho.ma", "type": "many_to_one"}, {"from": "dm_ngan.tu_ma", "to": "dm_tu.ma", "type": "many_to_one"}, {"from": "thong_tin_benh_nhan.doi_tuong_ma", "to": "dm_doi_tuong.ma", "type": "many_to_one"}, {"from": "thong_tin_benh_nhan.loai_benh_an_ma", "to": "dm_loai_benh_an.ma", "type": "many_to_one"}, {"from": "thong_tin_benh_nhan.nghe_nghiep", "to": "dm_nghe_nghiep.ma", "type": "many_to_one"}, {"from": "ho_so_luu_tru.trang_thai_ho_so_ma", "to": "dm_trang_thai_ho_so.ma", "type": "many_to_one"}], "pii_fields": ["thong_tin_benh_nhan.ho_ten", "thong_tin_benh_nhan.dia_chi", "danh_sach_benh_nhan.ten_benh_nhan", "danh_sach_benh_nhan.dia_chi"], "row_count_estimate": 128450, "extracted_at": "2025-11-04T09:12:00+07:00"}'::jsonb, '0999689b-6468-5316-83b1-0d376db6ff00', '2025-11-04 09:12:00+07'::timestamptz, '2025-11-04 09:12:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'VIMES - Danh mục dùng chung (Master Data)', 'EXCEL', 'File Excel mô tả cấu trúc dữ liệu và danh mục dùng chung (Giới tính, Khoa, Đối tượng, Trạng thái hồ sơ, Kho/Tủ/Ngăn) do phòng CNTT bệnh viện cung cấp.', '/uploads/vimes/VIMES_Patient_Record_Cau_truc_du_lieu_2.xlsx', '{"source_system": "VIMES - Danh mục dùng chung (Master Data)", "tables": [{"name": "dm_gioi_tinh", "description": "Danh mục giới tính. Áp dụng cho trường Giới (Sheet 1, Sheet 4) / Giới tính (Sheet 2)", "columns": [{"name": "ma", "data_type": "varchar(2)"}, {"name": "ten_hien_thi", "data_type": "varchar(20)"}], "sample_rows": [{"ma": "1", "ten_hien_thi": "Nam"}, {"ma": "2", "ten_hien_thi": "Nữ"}]}, {"name": "dm_khoa", "description": "Danh mục khoa/phòng bệnh viện. Áp dụng cho trường Vào từ khoa / Ra từ khoa (Sheet 1, Sheet 3, Sheet 4)", "columns": [{"name": "ma_khoa", "data_type": "varchar(10)"}, {"name": "ten_khoa", "data_type": "varchar(100)"}], "sample_rows": [{"ma_khoa": "A1", "ten_khoa": "Khoa A1 - Nội tổng hợp"}, {"ma_khoa": "A2", "ten_khoa": "Khoa A2 - Chấn thương chỉnh hình"}, {"ma_khoa": "A6", "ten_khoa": "Khoa A6 - Huyết học lâm sàng"}, {"ma_khoa": "A7", "ten_khoa": "Khoa A7 - Nội thận - Tiết niệu"}, {"ma_khoa": "A8", "ten_khoa": "Khoa A8 - Da liễu"}, {"ma_khoa": "A15", "ten_khoa": "Khoa A15 - Nội tổng hợp"}, {"ma_khoa": "A16", "ten_khoa": "Khoa A16 - Quốc tế"}, {"ma_khoa": "B1-A", "ten_khoa": "Khoa B1-A - Chẩn đoán hình ảnh (CT-Can thiệp)"}, {"ma_khoa": "B1-C", "ten_khoa": "Khoa B1-C - Phẫu thuật"}, {"ma_khoa": "B3", "ten_khoa": "Khoa B3 - Ngoại tổng hợp"}, {"ma_khoa": "B6", "ten_khoa": "Khoa B6 - Ngoại chấn thương"}, {"ma_khoa": "B9", "ten_khoa": "Khoa B9 - Tai - Mũi - Họng"}, {"ma_khoa": "XT", "ten_khoa": "Khoa Xạ trị"}, {"ma_khoa": "KB", "ten_khoa": "Khoa Khám bệnh"}], "note": "Danh sách khoa chỉ là ví dụ minh họa; cần đối chiếu danh mục khoa thực tế của bệnh viện trước khi đưa vào CSDL chính thức."}, {"name": "dm_doi_tuong", "description": "Danh mục đối tượng chi trả viện phí. Áp dụng cho trường Đối tượng (Sheet 2)", "columns": [{"name": "ma", "data_type": "varchar(20)"}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "BHYT", "ten_hien_thi": "BHYT"}, {"ma": "BHYT_QUAN", "ten_hien_thi": "BHYT Quân"}, {"ma": "VP", "ten_hien_thi": "Viện phí (Tự trả)"}, {"ma": "DV", "ten_hien_thi": "Dịch vụ"}, {"ma": "MP", "ten_hien_thi": "Miễn phí"}]}, {"name": "dm_loai_benh_an", "description": "Danh mục loại bệnh án. Áp dụng cho trường Loại (Sheet 2)", "columns": [{"name": "ma", "data_type": "varchar(10)"}, {"name": "ten_hien_thi", "data_type": "varchar(100)"}], "sample_rows": [{"ma": "NGT", "ten_hien_thi": "Bệnh án điều trị ngoại trú"}, {"ma": "NOI", "ten_hien_thi": "Bệnh án điều trị nội trú"}]}, {"name": "dm_trang_thai_ho_so", "description": "Danh mục trạng thái hồ sơ lưu trữ. Áp dụng cho trường Trạng thái hồ sơ (Sheet 3)", "columns": [{"name": "ma", "data_type": "varchar(10)"}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "DLT", "ten_hien_thi": "Hồ sơ đang lưu trữ"}, {"ma": "DM", "ten_hien_thi": "Hồ sơ đang mượn"}, {"ma": "CDH", "ten_hien_thi": "Hồ sơ chờ đưa vào kho"}, {"ma": "DH", "ten_hien_thi": "Hồ sơ đã hủy"}]}, {"name": "dm_kho", "description": "Danh mục kho lưu trữ. Áp dụng cho trường Kho (Sheet 3). Quan hệ phân cấp: Kho (1) - Tủ (n) - Ngăn (n), mỗi Tủ thuộc 1 Kho, mỗi Ngăn thuộc 1 Tủ.", "columns": [{"name": "ma", "data_type": "varchar(10)"}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "K1", "ten_hien_thi": "Kho 1"}, {"ma": "K2", "ten_hien_thi": "Kho 2"}, {"ma": "K3", "ten_hien_thi": "Kho 3"}]}, {"name": "dm_tu", "description": "Danh mục tủ lưu trữ, mỗi tủ thuộc 1 kho. Áp dụng cho trường Tủ (Sheet 3)", "columns": [{"name": "ma", "data_type": "varchar(20)"}, {"name": "kho_ma", "data_type": "varchar(10)", "foreign_key": {"references": "dm_kho.ma"}}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "T-K1-A", "ten_hien_thi": "Tủ A (thuộc Kho 1)"}, {"ma": "T-K1-B", "ten_hien_thi": "Tủ B (thuộc Kho 1)"}, {"ma": "T-K2-A", "ten_hien_thi": "Tủ A (thuộc Kho 2)"}]}, {"name": "dm_ngan", "description": "Danh mục ngăn lưu trữ, mỗi ngăn thuộc 1 tủ. Áp dụng cho trường Ngăn (Sheet 3)", "columns": [{"name": "ma", "data_type": "varchar(20)"}, {"name": "tu_ma", "data_type": "varchar(20)", "foreign_key": {"references": "dm_tu.ma"}}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "N-TA-1", "ten_hien_thi": "Ngăn 1 (thuộc Tủ A)"}, {"ma": "N-TA-2", "ten_hien_thi": "Ngăn 2 (thuộc Tủ A)"}, {"ma": "N-TA-3", "ten_hien_thi": "Ngăn 3 (thuộc Tủ A)"}]}, {"name": "dm_nghe_nghiep", "description": "Danh mục nghề nghiệp (tùy chọn, có thể để dạng Text tự do). Áp dụng cho trường Nghề nghiệp (Sheet 2)", "columns": [{"name": "ma", "data_type": "varchar(10)"}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}], "sample_rows": [{"ma": "BD", "ten_hien_thi": "Bộ đội"}, {"ma": "CNVC", "ten_hien_thi": "Cán bộ - công chức - viên chức"}, {"ma": "CN", "ten_hien_thi": "Công nhân"}, {"ma": "ND", "ten_hien_thi": "Nông dân"}, {"ma": "HSSV", "ten_hien_thi": "Học sinh - Sinh viên"}, {"ma": "HT", "ten_hien_thi": "Hưu trí"}, {"ma": "TD", "ten_hien_thi": "Tự do"}, {"ma": "K", "ten_hien_thi": "Khác"}]}], "note": "Ánh xạ trực tiếp từ sheet ''5.Danh muc (Master Data)'' trong tài liệu cấu trúc dữ liệu VIMES do người dùng cung cấp. Đã bổ sung đầy đủ 9 danh mục (trước đó chỉ có 4/9) và đầy đủ toàn bộ mã khoa (14/14) thay vì chỉ trích mẫu."}'::jsonb, '6c568dc6-50ba-5919-8086-31e12eb53326', '2025-11-04 09:20:00+07'::timestamptz, '2025-11-04 09:20:00+07'::timestamptz),
  ('84bdeb46-0eba-564e-8437-833ede4e2718', 'VIMES Patient Record - Lượt khám & chẩn đoán', 'SQL', 'Trích xuất bảng lượt khám, chẩn đoán ICD-10 và đối tượng chi trả từ hệ thống VIMES cho mục đích phân tích lượt khám.', 'sqlserver://vimes-prod-replica.hospital.local:1433/VIMES_PatientRecord', '{"source_system": "VIMES Patient Record - Module Hồ sơ lưu trữ", "tables": [{"name": "ho_so_luu_tru", "description": "Hồ sơ bệnh án đã được lưu trữ vật lý (Sheet 3 - Thông tin hồ sơ lưu trữ)", "columns": [{"name": "so_benh_an", "data_type": "varchar(30)", "primary_key": true, "required": true, "note": "Định dạng NGTBD-nnn hoặc NOI-nnn, duy nhất theo đợt điều trị"}, {"name": "so_ho_so", "data_type": "integer", "required": true, "foreign_key": {"references": "danh_sach_benh_nhan.so_ho_so"}}, {"name": "thoi_gian_vao_vien", "data_type": "timestamp", "required": true}, {"name": "ngay_ra_vien", "data_type": "date", "required": false, "note": ">= thoi_gian_vao_vien nếu có"}, {"name": "khoa_vao_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "khoa_ra_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "chan_doan", "data_type": "varchar(250)", "required": false}, {"name": "so_luu_tru", "data_type": "integer", "primary_key": false, "required": true, "note": "Duy nhất trong phạm vi kho lưu trữ"}, {"name": "ngay_luu_tru", "data_type": "timestamp", "required": true, "note": ">= ngay_ra_vien"}, {"name": "trang_thai_ho_so_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_trang_thai_ho_so.ma"}}, {"name": "kho_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_kho.ma"}}, {"name": "tu_ma", "data_type": "varchar(20)", "required": true, "foreign_key": {"references": "dm_tu.ma"}}, {"name": "ngan_ma", "data_type": "varchar(20)", "required": true, "foreign_key": {"references": "dm_ngan.ma"}}, {"name": "vi_tri", "data_type": "varchar(50)", "required": false, "note": "VD: Kệ 2 - Hàng 5"}, {"name": "ky_hieu", "data_type": "varchar(20)", "required": false}, {"name": "ghi_chu", "data_type": "varchar(500)", "required": false}]}, {"name": "thong_tin_benh_nhan", "description": "Thông tin hành chính bệnh nhân gắn với bệnh án (Sheet 2)", "columns": [{"name": "so_ho_so", "data_type": "integer", "primary_key": true, "required": true}, {"name": "so_benh_an", "data_type": "varchar(30)", "required": true, "foreign_key": {"references": "ho_so_luu_tru.so_benh_an"}}, {"name": "ho_ten", "data_type": "varchar(100)", "required": true, "pii": true}, {"name": "tuoi", "data_type": "integer", "required": true, "note": "0-130"}, {"name": "gioi_tinh_ma", "data_type": "varchar(2)", "required": true, "foreign_key": {"references": "dm_gioi_tinh.ma"}}, {"name": "dia_chi", "data_type": "varchar(250)", "required": false, "pii": true}, {"name": "nghe_nghiep", "data_type": "varchar(100)", "required": false, "foreign_key": {"references": "dm_nghe_nghiep.ma", "nullable": true}}, {"name": "doi_tuong_ma", "data_type": "varchar(20)", "required": true, "foreign_key": {"references": "dm_doi_tuong.ma"}}, {"name": "loai_benh_an_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_loai_benh_an.ma"}}]}, {"name": "danh_sach_benh_nhan", "description": "Danh sách tổng hợp toàn bộ bệnh nhân đã lưu trữ hồ sơ (Sheet 4 - dùng cho grid tổng hợp/báo cáo)", "columns": [{"name": "so_ho_so", "data_type": "integer", "primary_key": true, "required": true}, {"name": "so_luu_tru", "data_type": "integer", "required": true}, {"name": "ten_benh_nhan", "data_type": "varchar(100)", "required": true, "pii": true}, {"name": "tuoi", "data_type": "integer", "required": true}, {"name": "gioi_tinh_ma", "data_type": "varchar(2)", "required": true, "foreign_key": {"references": "dm_gioi_tinh.ma"}}, {"name": "dia_chi", "data_type": "varchar(250)", "required": false, "pii": true}, {"name": "thoi_gian_vao_vien", "data_type": "date", "required": true}, {"name": "ngay_ra", "data_type": "date", "required": false}, {"name": "khoa_vao_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "khoa_ra_ma", "data_type": "varchar(10)", "required": true, "foreign_key": {"references": "dm_khoa.ma_khoa"}}, {"name": "chan_doan", "data_type": "varchar(250)", "required": false}]}, {"name": "dm_gioi_tinh", "description": "Danh mục giới tính", "columns": [{"name": "ma", "data_type": "varchar(2)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(20)"}]}, {"name": "dm_khoa", "description": "Danh mục khoa/phòng bệnh viện", "columns": [{"name": "ma_khoa", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_khoa", "data_type": "varchar(100)"}]}, {"name": "dm_doi_tuong", "description": "Danh mục đối tượng chi trả viện phí", "columns": [{"name": "ma", "data_type": "varchar(20)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}]}, {"name": "dm_loai_benh_an", "description": "Danh mục loại bệnh án", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(100)"}]}, {"name": "dm_trang_thai_ho_so", "description": "Danh mục trạng thái hồ sơ lưu trữ", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}]}, {"name": "dm_kho", "description": "Danh mục kho lưu trữ", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}]}, {"name": "dm_tu", "description": "Danh mục tủ lưu trữ (thuộc 1 kho)", "columns": [{"name": "ma", "data_type": "varchar(20)", "primary_key": true}, {"name": "kho_ma", "data_type": "varchar(10)", "foreign_key": {"references": "dm_kho.ma"}}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}]}, {"name": "dm_ngan", "description": "Danh mục ngăn lưu trữ (thuộc 1 tủ)", "columns": [{"name": "ma", "data_type": "varchar(20)", "primary_key": true}, {"name": "tu_ma", "data_type": "varchar(20)", "foreign_key": {"references": "dm_tu.ma"}}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}]}, {"name": "dm_nghe_nghiep", "description": "Danh mục nghề nghiệp (tùy chọn, có thể tự do dạng text)", "columns": [{"name": "ma", "data_type": "varchar(10)", "primary_key": true}, {"name": "ten_hien_thi", "data_type": "varchar(50)"}]}], "relationships": [{"from": "ho_so_luu_tru.so_ho_so", "to": "danh_sach_benh_nhan.so_ho_so", "type": "many_to_one"}, {"from": "thong_tin_benh_nhan.so_benh_an", "to": "ho_so_luu_tru.so_benh_an", "type": "one_to_one"}, {"from": "ho_so_luu_tru.khoa_vao_ma", "to": "dm_khoa.ma_khoa", "type": "many_to_one"}, {"from": "ho_so_luu_tru.khoa_ra_ma", "to": "dm_khoa.ma_khoa", "type": "many_to_one"}, {"from": "ho_so_luu_tru.kho_ma", "to": "dm_kho.ma", "type": "many_to_one"}, {"from": "ho_so_luu_tru.tu_ma", "to": "dm_tu.ma", "type": "many_to_one"}, {"from": "ho_so_luu_tru.ngan_ma", "to": "dm_ngan.ma", "type": "many_to_one"}, {"from": "dm_tu.kho_ma", "to": "dm_kho.ma", "type": "many_to_one"}, {"from": "dm_ngan.tu_ma", "to": "dm_tu.ma", "type": "many_to_one"}, {"from": "thong_tin_benh_nhan.doi_tuong_ma", "to": "dm_doi_tuong.ma", "type": "many_to_one"}, {"from": "thong_tin_benh_nhan.loai_benh_an_ma", "to": "dm_loai_benh_an.ma", "type": "many_to_one"}, {"from": "ho_so_luu_tru.trang_thai_ho_so_ma", "to": "dm_trang_thai_ho_so.ma", "type": "many_to_one"}], "pii_fields": ["thong_tin_benh_nhan.ho_ten", "thong_tin_benh_nhan.dia_chi", "danh_sach_benh_nhan.ten_benh_nhan", "danh_sach_benh_nhan.dia_chi"], "row_count_estimate": 128450, "extracted_at": "2025-11-04T09:12:00+07:00"}'::jsonb, 'ac89f7ff-da2d-5a3d-9c94-a41fe886a788', '2025-12-10 10:15:00+07'::timestamptz, '2025-12-10 10:15:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', 'Core Banking - Giao dịch & Tài khoản', 'SQL', 'Kết nối trực tiếp tới Core Banking (Oracle) lấy dữ liệu khách hàng, tài khoản và giao dịch hàng ngày.', 'oracle://corebanking.internal:1521/CBSPROD', '{"tables": [{"name": "customers", "columns": [{"name": "customer_id", "data_type": "bigint", "primary_key": true}, {"name": "full_name", "data_type": "varchar(150)", "pii": true}, {"name": "national_id", "data_type": "varchar(20)", "pii": true}, {"name": "phone", "data_type": "varchar(15)", "pii": true}, {"name": "customer_segment", "data_type": "varchar(30)"}, {"name": "credit_score", "data_type": "integer"}]}, {"name": "accounts", "columns": [{"name": "account_no", "data_type": "varchar(20)", "primary_key": true, "pii": true}, {"name": "customer_id", "data_type": "bigint", "foreign_key": {"references": "customers.customer_id"}}, {"name": "account_type", "data_type": "varchar(20)"}, {"name": "balance", "data_type": "numeric(18,2)"}, {"name": "open_date", "data_type": "date"}]}, {"name": "transactions", "columns": [{"name": "transaction_id", "data_type": "bigint", "primary_key": true}, {"name": "account_no", "data_type": "varchar(20)", "foreign_key": {"references": "accounts.account_no"}}, {"name": "channel", "data_type": "varchar(20)", "note": "ATM, IB, POS, MOBILE"}, {"name": "amount", "data_type": "numeric(18,2)"}, {"name": "transaction_time", "data_type": "timestamp"}, {"name": "is_flagged", "data_type": "boolean"}]}], "relationships": [{"from": "accounts.customer_id", "to": "customers.customer_id", "type": "many_to_one"}, {"from": "transactions.account_no", "to": "accounts.account_no", "type": "many_to_one"}], "row_count_estimate": 2400000}'::jsonb, '0d250b43-72b6-59c3-9a28-834d75af393f', '2025-11-08 08:45:00+07'::timestamptz, '2025-11-08 08:45:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', 'CRM - Hồ sơ khách hàng', 'JSON', 'Export định kỳ dạng JSON từ hệ thống CRM chứa thông tin phân khúc khách hàng và điểm tín dụng nội bộ.', 's3://bank-data-lake/crm/customer_profile/', '{"tables": [{"name": "customer_profile.json", "columns": [{"name": "customer_id", "data_type": "bigint"}, {"name": "segment", "data_type": "string"}, {"name": "risk_score", "data_type": "integer"}, {"name": "kyc_status", "data_type": "string"}]}], "row_count_estimate": 980000}'::jsonb, 'aa87a790-835d-5d2e-82f2-a6758588dda5', '2025-11-09 09:00:00+07'::timestamptz, '2025-11-09 09:00:00+07'::timestamptz),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d', 'POS - Dữ liệu bán hàng tại quầy', 'CSV', 'File CSV xuất hàng ngày từ 120 cửa hàng, chứa chi tiết hóa đơn bán hàng theo SKU.', 'sftp://pos-export.retailchain.vn/daily/', '{"tables": [{"name": "pos_transactions.csv", "columns": [{"name": "invoice_no", "data_type": "string"}, {"name": "store_code", "data_type": "string"}, {"name": "sku", "data_type": "string"}, {"name": "category", "data_type": "string"}, {"name": "qty", "data_type": "integer"}, {"name": "unit_price", "data_type": "float"}, {"name": "discount_pct", "data_type": "float"}, {"name": "sold_at", "data_type": "datetime"}]}, {"name": "stores.csv", "columns": [{"name": "store_code", "data_type": "string", "primary_key": true}, {"name": "region", "data_type": "string"}, {"name": "store_type", "data_type": "string"}]}], "relationships": [{"from": "pos_transactions.csv.store_code", "to": "stores.csv.store_code", "type": "many_to_one"}], "delimiter": ",", "encoding": "UTF-8", "row_count_estimate": 5600000}'::jsonb, 'f46d150c-c76d-5b15-8c79-46f130fbd6fe', '2025-11-11 09:30:00+07'::timestamptz, '2025-11-11 09:30:00+07'::timestamptz),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d', 'Sàn TMĐT nội bộ - Đơn hàng online', 'JSON', 'API export đơn hàng từ nền tảng thương mại điện tử nội bộ của chuỗi siêu thị.', 'https://api.retailchain.vn/v2/orders/export', '{"tables": [{"name": "online_orders", "columns": [{"name": "order_id", "data_type": "string"}, {"name": "sku", "data_type": "string"}, {"name": "qty", "data_type": "integer"}, {"name": "total_amount", "data_type": "float"}, {"name": "created_at", "data_type": "datetime"}]}], "row_count_estimate": 1200000}'::jsonb, '1ba6a112-bf9f-52ae-b631-28fee8d3f1d6', '2025-11-12 10:00:00+07'::timestamptz, '2025-11-12 10:00:00+07'::timestamptz),
  ('18525676-8c6b-552b-8de7-a50899ef4b92', 'TMS - Hệ thống quản lý vận tải', 'SQL', 'Kết nối tới hệ thống Transportation Management System (PostgreSQL) lấy dữ liệu vận đơn và đối tác vận chuyển.', 'postgresql://tms-db.logistics.local:5432/tms_prod', '{"tables": [{"name": "shipments", "columns": [{"name": "shipment_id", "data_type": "string", "primary_key": true}, {"name": "route_code", "data_type": "string"}, {"name": "carrier_id", "data_type": "string"}, {"name": "origin_hub", "data_type": "string"}, {"name": "dest_hub", "data_type": "string"}, {"name": "pickup_time", "data_type": "timestamp"}, {"name": "delivered_time", "data_type": "timestamp"}, {"name": "sla_hours", "data_type": "integer"}, {"name": "status", "data_type": "string"}]}, {"name": "carriers", "columns": [{"name": "carrier_id", "data_type": "string", "primary_key": true}, {"name": "carrier_name", "data_type": "string"}, {"name": "vehicle_type", "data_type": "string"}]}], "relationships": [{"from": "shipments.carrier_id", "to": "carriers.carrier_id", "type": "many_to_one"}], "row_count_estimate": 890000}'::jsonb, 'db01c8cc-3651-5089-bd1f-d07ff5d7deb4', '2025-11-18 11:20:00+07'::timestamptz, '2025-11-18 11:20:00+07'::timestamptz),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277', 'Hệ thống Quản lý Đào tạo - Sinh viên', 'EXCEL', 'File Excel tổng hợp danh sách sinh viên, điểm và trạng thái tốt nghiệp do Phòng Đào tạo cung cấp theo học kỳ.', '/uploads/edu/danh_sach_sinh_vien_2025_hk1.xlsx', '{"tables": [{"name": "students", "columns": [{"name": "student_code", "data_type": "varchar(15)", "primary_key": true}, {"name": "full_name", "data_type": "varchar(100)", "pii": true}, {"name": "faculty_code", "data_type": "varchar(10)", "foreign_key": {"references": "faculties.faculty_code"}}, {"name": "admission_year", "data_type": "integer"}, {"name": "gpa", "data_type": "numeric(3,2)"}, {"name": "graduation_status", "data_type": "varchar(20)"}]}, {"name": "faculties", "columns": [{"name": "faculty_code", "data_type": "varchar(10)", "primary_key": true}, {"name": "faculty_name", "data_type": "varchar(100)"}]}], "relationships": [{"from": "students.faculty_code", "to": "faculties.faculty_code", "type": "many_to_one"}], "row_count_estimate": 18500}'::jsonb, '45072fdd-d2d0-5d67-bc7d-5f8250bf82bb', '2025-12-02 09:00:00+07'::timestamptz, '2025-12-02 09:00:00+07'::timestamptz),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48', 'MES - Dữ liệu sản xuất theo ca', 'JSON', 'Dữ liệu sự kiện sản xuất theo thời gian thực từ hệ thống MES, xuất theo batch JSON mỗi 15 phút.', 's3://mfg-data-lake/mes/production_events/', '{"tables": [{"name": "production_events", "columns": [{"name": "event_id", "data_type": "bigint", "primary_key": true}, {"name": "line_code", "data_type": "varchar(10)"}, {"name": "shift_code", "data_type": "varchar(5)"}, {"name": "planned_units", "data_type": "integer"}, {"name": "produced_units", "data_type": "integer"}, {"name": "defect_units", "data_type": "integer"}, {"name": "downtime_minutes", "data_type": "integer"}, {"name": "event_time", "data_type": "timestamp"}]}], "relationships": [], "source_protocol": "MQTT -> batch export JSON", "row_count_estimate": 340000}'::jsonb, '17e2d3cb-682c-5184-be4d-954dc729419c', '2025-12-08 13:20:00+07'::timestamptz, '2025-12-08 13:20:00+07'::timestamptz),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594', 'Hệ thống Hợp đồng & Bồi thường', 'SQL', 'Trích xuất dữ liệu hợp đồng bảo hiểm và hồ sơ yêu cầu bồi thường từ hệ thống lõi bảo hiểm.', 'sqlserver://policy-core.insureco.vn:1433/PolicyCore', '{"tables": [{"name": "policies", "columns": [{"name": "policy_no", "data_type": "varchar(20)", "primary_key": true}, {"name": "product_code", "data_type": "varchar(10)"}, {"name": "holder_name", "data_type": "varchar(100)", "pii": true}, {"name": "sum_assured", "data_type": "numeric(18,2)"}, {"name": "issue_date", "data_type": "date"}]}, {"name": "claims", "columns": [{"name": "claim_id", "data_type": "varchar(20)", "primary_key": true}, {"name": "policy_no", "data_type": "varchar(20)", "foreign_key": {"references": "policies.policy_no"}}, {"name": "claim_amount", "data_type": "numeric(18,2)"}, {"name": "claim_status", "data_type": "varchar(20)"}, {"name": "filed_date", "data_type": "date"}, {"name": "is_suspected_fraud", "data_type": "boolean"}]}], "relationships": [{"from": "claims.policy_no", "to": "policies.policy_no", "type": "many_to_one"}], "row_count_estimate": 210000}'::jsonb, 'eea70fb1-adaa-5b4c-a360-9fe710e5e011', '2025-10-20 08:20:00+07'::timestamptz, '2025-10-20 08:20:00+07'::timestamptz),
  ('f8c4432f-0252-5275-a581-958039b98639', 'Billing - Cước & lưu lượng thuê bao', 'CSV', 'File CSV xuất hàng ngày từ hệ thống tính cước (Billing) chứa lưu lượng data/thoại và doanh thu ARPU theo thuê bao.', 'sftp://billing-export.telco.vn/daily_usage/', '{"tables": [{"name": "subscribers", "columns": [{"name": "msisdn", "data_type": "varchar(15)", "primary_key": true, "pii": true}, {"name": "plan_code", "data_type": "varchar(10)"}, {"name": "region", "data_type": "varchar(30)"}, {"name": "activation_date", "data_type": "date"}, {"name": "status", "data_type": "varchar(15)"}]}, {"name": "usage_daily", "columns": [{"name": "msisdn", "data_type": "varchar(15)", "foreign_key": {"references": "subscribers.msisdn"}}, {"name": "usage_date", "data_type": "date"}, {"name": "data_mb", "data_type": "numeric(12,2)"}, {"name": "voice_minutes", "data_type": "numeric(10,2)"}, {"name": "arpu", "data_type": "numeric(12,2)"}]}], "relationships": [{"from": "usage_daily.msisdn", "to": "subscribers.msisdn", "type": "many_to_one"}], "row_count_estimate": 41000000}'::jsonb, '1951bbd1-55d5-5bdc-a11b-4150696b0c07', '2025-12-15 09:45:00+07'::timestamptz, '2025-12-15 09:45:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', 'Clickstream - Hành vi người dùng', 'JSON', 'Dữ liệu clickstream (session, sự kiện giỏ hàng) thu thập qua Segment, lưu trên S3 theo định dạng JSON Lines.', 's3://ecom-data-lake/clickstream/events/', '{"tables": [{"name": "sessions", "columns": [{"name": "session_id", "data_type": "string", "primary_key": true}, {"name": "user_id", "data_type": "string"}, {"name": "channel", "data_type": "string"}, {"name": "started_at", "data_type": "timestamp"}, {"name": "device", "data_type": "string"}]}, {"name": "cart_events", "columns": [{"name": "event_id", "data_type": "string", "primary_key": true}, {"name": "session_id", "data_type": "string", "foreign_key": {"references": "sessions.session_id"}}, {"name": "sku", "data_type": "string"}, {"name": "category", "data_type": "string"}, {"name": "event_type", "data_type": "string", "note": "add_to_cart, remove_from_cart, checkout, purchase"}, {"name": "event_time", "data_type": "timestamp"}]}, {"name": "ad_spend", "columns": [{"name": "campaign_id", "data_type": "string", "primary_key": true}, {"name": "channel", "data_type": "string"}, {"name": "spend", "data_type": "numeric(14,2)"}, {"name": "clicks", "data_type": "integer"}, {"name": "conversions", "data_type": "integer"}, {"name": "report_date", "data_type": "date"}]}], "relationships": [{"from": "cart_events.session_id", "to": "sessions.session_id", "type": "many_to_one"}], "row_count_estimate": 7300000}'::jsonb, 'eda2a896-1250-56e5-b7bd-b8162f8af175', '2026-01-05 10:20:00+07'::timestamptz, '2026-01-05 10:20:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', 'Ad Platforms - Chi phí quảng cáo', 'TEXT', 'Báo cáo chi phí quảng cáo tổng hợp hàng tuần từ Facebook Ads, Google Ads, xuất dạng file TXT phân tách bởi tab.', '/uploads/ecom/weekly_ad_spend_report.txt', '{"tables": [{"name": "weekly_ad_spend_report.txt", "columns": [{"name": "campaign_id", "data_type": "string"}, {"name": "channel", "data_type": "string"}, {"name": "spend", "data_type": "float"}, {"name": "conversions", "data_type": "integer"}]}], "delimiter": "\\t", "row_count_estimate": 5200}'::jsonb, '42c154dd-20cb-554a-9822-c76543a5e552', '2026-01-06 10:00:00+07'::timestamptz, '2026-01-06 10:00:00+07'::timestamptz);

-- ============================================================
-- 7. PROJECT_SESSIONS
-- ============================================================
INSERT INTO public.project_sessions (project_id, user_id, title, status, id, created_at, updated_at) VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'a678ac27-3077-5ef2-8919-5218b2e48791', 'Thiết kế Data Warehouse Hồ sơ lưu trữ v1', 'COMPLETED', '9573f767-f342-56c0-90bc-c88ff63ee157', '2025-11-04 09:30:00+07'::timestamptz, '2025-11-04 11:45:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', '15c1be82-ea36-5205-af17-7fb5947c2027', 'Điều chỉnh mô hình sau review PII', 'COMPLETED', 'f0d5354c-0c59-5e4e-816e-1310ff9a1181', '2025-11-06 14:00:00+07'::timestamptz, '2025-11-06 16:10:00+07'::timestamptz),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'a678ac27-3077-5ef2-8919-5218b2e48791', 'Bổ sung phân tích tỷ lệ lấp đầy kho', 'ACTIVE', '2d2884f5-138f-5885-8d75-38aff890d4d0', '2026-08-10 15:30:00+07'::timestamptz, '2026-08-10 16:20:00+07'::timestamptz),
  ('84bdeb46-0eba-564e-8437-833ede4e2718', 'a678ac27-3077-5ef2-8919-5218b2e48791', 'Thiết kế data mart lượt khám & chẩn đoán', 'ACTIVE', '3e80b14d-234b-550d-8103-dd9ef82ea1c8', '2025-12-10 10:10:00+07'::timestamptz, '2025-12-10 12:00:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', '729525be-38aa-50fd-8ea9-3fedf76615f1', 'Thiết kế DW rủi ro tín dụng - phiên 1', 'COMPLETED', '7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', '2025-11-08 09:00:00+07'::timestamptz, '2025-11-08 12:30:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', '0740e12f-bc1c-556f-9cc7-3ec5332e692e', 'Rà soát mã hóa PII giao dịch', 'ACTIVE', '2b2907f2-91bf-578a-acb2-391081d6789e', '2026-08-05 13:30:00+07'::timestamptz, '2026-08-05 14:10:00+07'::timestamptz),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d', '0740e12f-bc1c-556f-9cc7-3ec5332e692e', 'Thiết kế fact bán hàng đa kênh', 'COMPLETED', '7545fdc0-c3e9-55f7-8278-32cb3b18b6ac', '2025-11-11 09:40:00+07'::timestamptz, '2025-11-11 11:55:00+07'::timestamptz),
  ('18525676-8c6b-552b-8de7-a50899ef4b92', 'c0445430-562e-5472-bea6-06f3a5d6f645', 'Thiết kế fact vận đơn & hiệu suất tài xế', 'COMPLETED', '166e77f4-5a73-57b3-b9ba-eae00c1a688e', '2025-11-18 11:10:00+07'::timestamptz, '2025-11-18 13:20:00+07'::timestamptz),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277', '15c1be82-ea36-5205-af17-7fb5947c2027', 'Thiết kế mô hình học vụ & tốt nghiệp', 'ACTIVE', '2040ae41-afa0-57f5-8d4c-1bdd26ea2754', '2025-12-02 09:10:00+07'::timestamptz, '2025-12-02 10:40:00+07'::timestamptz),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48', '4c507932-ae90-57a1-8765-885e45eba112', 'Thiết kế fact OEE theo dây chuyền', 'COMPLETED', '0c0a2c4f-c4f9-5f97-80d1-db681198f429', '2025-12-08 13:30:00+07'::timestamptz, '2025-12-08 15:45:00+07'::timestamptz),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594', '85651d6b-4cc0-56ba-ba15-ffc404f10abc', 'Thiết kế DW bồi thường bảo hiểm', 'ARCHIVED', '16f05d9a-1837-559b-bdb3-42b3a1ec9d73', '2025-10-20 08:30:00+07'::timestamptz, '2025-12-01 10:00:00+07'::timestamptz),
  ('f8c4432f-0252-5275-a581-958039b98639', 'e892c55a-77c6-5c8f-8e00-00da20839ba9', 'Thiết kế fact churn thuê bao', 'ACTIVE', '73e590b3-2cd1-589f-b310-75beab465dfd', '2025-12-15 10:00:00+07'::timestamptz, '2025-12-15 12:15:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', '25a6f954-f1cd-567d-88a0-630c4407b254', 'Thiết kế DW hành vi mua sắm & marketing', 'ACTIVE', '2fdb8582-49bc-5285-9d5e-2fa613de7d70', '2026-01-05 10:30:00+07'::timestamptz, '2026-01-05 13:00:00+07'::timestamptz);
-- ============================================================
-- 8. SESSION_EVENTS
-- ============================================================
INSERT INTO public.session_events (session_id, role, type, content, metadata, id, created_at, updated_at) VALUES
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'USER', 'MESSAGE', 'Tôi cần xây dựng Data Warehouse cho dữ liệu hồ sơ bệnh án lưu trữ của bệnh viện, dựa trên yêu cầu và dữ liệu nguồn tôi đã tải lên.', NULL, '79cddbf9-b604-54a4-9714-d27c90949d05', '2025-11-04 09:30:05+07'::timestamptz, '2025-11-04 09:30:05+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'MESSAGE', 'Đã nhận yêu cầu. Tôi sẽ điều phối các agent để phân tích requirement và dữ liệu nguồn trước khi thiết kế mô hình DW.', '{"model": "claude-sonnet-4-6"}'::jsonb, 'f01c1fee-1194-588b-9e1c-d40da8c5dcfb', '2025-11-04 09:30:20+07'::timestamptz, '2025-11-04 09:30:20+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'AGENT_CALL', NULL, '{"caller_agent": "OrchestrationAgent", "target_agent": "RequirementAgent", "input": {"project_id": "vimes-hs", "requirement_ids": ["req-vimes-hs-biz", "req-vimes-hs-an1", "req-vimes-hs-an2", "req-vimes-hs-tech"]}}'::jsonb, '2a7da704-99e7-5558-93b2-78a1fb8709bd', '2025-11-04 09:30:25+07'::timestamptz, '2025-11-04 09:30:25+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'TOOL_CALL', NULL, '{"agent": "RequirementAgent", "tool": "pii_guard.mask", "arguments": {"target": "raw_requirement_text"}}'::jsonb, '756177e3-ba00-50f7-9d64-66aeb99864e9', '2025-11-04 09:30:27+07'::timestamptz, '2025-11-04 09:30:27+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'TOOL', 'TOOL_RESULT', NULL, '{"session_event_id": "756177e3-ba00-50f7-9d64-66aeb99864e9", "tool": "pii_guard.mask", "status": "SUCCESS", "result": {"masked_fields": ["ho_ten", "dia_chi"], "masking_strategy": "hash_sha256"}}'::jsonb, 'af303b70-7247-5e8f-b034-ce29067dd1ea', '2025-11-04 09:30:29+07'::timestamptz, '2025-11-04 09:30:29+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'AGENT_RESULT', NULL, '{"session_event_id": "af303b70-7247-5e8f-b034-ce29067dd1ea", "agent": "RequirementAgent", "status": "SUCCESS", "output": {"analytical_requirements_extracted": 2, "metrics": ["Số lượng hồ sơ lưu trữ", "Tỷ lệ lấp đầy vị trí lưu trữ"]}, "llm": {"provider": "anthropic", "model": "claude-sonnet-4-6", "input_tokens": 2140, "output_tokens": 480, "total_tokens": 2620, "temperature": 0.3, "latency_ms": 3120, "finish_reason": "end_turn"}}'::jsonb, '6a186d5f-81ac-54a5-801e-e4743cc62784', '2025-11-04 09:31:10+07'::timestamptz, '2025-11-04 09:31:10+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'AGENT_CALL', NULL, '{"caller_agent": "OrchestrationAgent", "target_agent": "SourceDataAgent", "input": {"data_source_ids": ["ds-vimes-hs-main", "ds-vimes-hs-master"]}}'::jsonb, '77c5d40e-1963-5407-9e96-fcd96c7c480d', '2025-11-04 09:31:15+07'::timestamptz, '2025-11-04 09:31:15+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'TOOL_CALL', NULL, '{"agent": "SourceDataAgent", "tool": "schema_inspector.extract", "arguments": {"source": "ds-vimes-hs-main", "sample_rows": 500}}'::jsonb, '5f3a07da-71c7-5ca3-a7a3-edf97b45a56a', '2025-11-04 09:31:18+07'::timestamptz, '2025-11-04 09:31:18+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'TOOL', 'TOOL_RESULT', NULL, '{"session_event_id": "5f3a07da-71c7-5ca3-a7a3-edf97b45a56a", "tool": "schema_inspector.extract", "status": "SUCCESS", "result": {"tables_found": 11, "pii_columns_detected": ["ho_ten", "dia_chi", "ten_benh_nhan"]}}'::jsonb, '514c907a-e6bf-56da-b136-d1f211a049db', '2025-11-04 09:31:40+07'::timestamptz, '2025-11-04 09:31:40+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'AGENT_RESULT', NULL, '{"session_event_id": "514c907a-e6bf-56da-b136-d1f211a049db", "agent": "SourceDataAgent", "status": "SUCCESS", "output": {"tables_analyzed": 11, "relationships_inferred": 12}, "llm": {"provider": "anthropic", "model": "claude-sonnet-4-6", "input_tokens": 5230, "output_tokens": 910, "total_tokens": 6140, "temperature": 0.2, "latency_ms": 4870, "finish_reason": "end_turn"}}'::jsonb, '30098c13-275c-5ef8-a4f5-839ea875480a', '2025-11-04 09:32:30+07'::timestamptz, '2025-11-04 09:32:30+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'AGENT_CALL', NULL, '{"caller_agent": "OrchestrationAgent", "target_agent": "DWDesignAgent", "input": {"analytical_requirements": 2, "source_tables": 11}}'::jsonb, '2eca7814-84de-5cfa-a4c1-07b353e262fa', '2025-11-04 09:32:35+07'::timestamptz, '2025-11-04 09:32:35+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'AGENT_RESULT', NULL, '{"session_event_id": "2eca7814-84de-5cfa-a4c1-07b353e262fa", "agent": "DWDesignAgent", "status": "SUCCESS", "output": {"dbml_generated": true, "fact_tables": ["fact_ho_so_luu_tru"], "dim_tables": 6}, "llm": {"provider": "anthropic", "model": "claude-sonnet-4-6", "input_tokens": 8900, "output_tokens": 2100, "total_tokens": 11000, "temperature": 0.4, "latency_ms": 9210, "finish_reason": "end_turn"}}'::jsonb, '24badbbf-fadb-5dd9-95b0-2893cddaa750', '2025-11-04 09:35:00+07'::timestamptz, '2025-11-04 09:35:00+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'TOOL_CALL', NULL, '{"agent": "ValidationEngine", "tool": "dbml_validate", "arguments": {"revision_candidate": 1}}'::jsonb, 'c239f853-5a7b-50cc-ae88-a9479ec3b8ce', '2025-11-04 09:35:05+07'::timestamptz, '2025-11-04 09:35:05+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'TOOL', 'TOOL_RESULT', NULL, '{"session_event_id": "c239f853-5a7b-50cc-ae88-a9479ec3b8ce", "tool": "dbml_validate", "status": "FAILED", "error": "Syntax error: table ''dim_khoa'' thiếu dấu đóng ngoặc tại dòng 42"}'::jsonb, '02f5aa98-c649-5444-a8f8-8fa7324d08ac', '2025-11-04 09:35:08+07'::timestamptz, '2025-11-04 09:35:08+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'MESSAGE', 'Phát hiện lỗi cú pháp DBML, đang yêu cầu DWDesignAgent tái tạo lại thiết kế (retry).', '{"model": "claude-sonnet-4-6"}'::jsonb, '44e69970-bd43-5ed4-8cea-0fc4b60a980a', '2025-11-04 09:35:12+07'::timestamptz, '2025-11-04 09:35:12+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'TOOL_CALL', NULL, '{"agent": "ValidationEngine", "tool": "dbml_validate", "arguments": {"revision_candidate": 1, "attempt": 2}}'::jsonb, '0214f42b-4fd1-55e2-bcfe-55b9ba605ad1', '2025-11-04 09:36:40+07'::timestamptz, '2025-11-04 09:36:40+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'TOOL', 'TOOL_RESULT', NULL, '{"session_event_id": "0214f42b-4fd1-55e2-bcfe-55b9ba605ad1", "tool": "dbml_validate", "status": "SUCCESS", "result": {"syntax_ok": true, "warnings": 0}}'::jsonb, 'be584b6f-ed17-52b6-b510-21e9d979f591', '2025-11-04 09:36:43+07'::timestamptz, '2025-11-04 09:36:43+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'TOOL_CALL', NULL, '{"agent": "Sandbox", "tool": "sandbox_run_ddl", "arguments": {"revision_candidate": 1}}'::jsonb, 'db1a3414-faa1-5de0-9587-a0baab72a90e', '2025-11-04 09:36:50+07'::timestamptz, '2025-11-04 09:36:50+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'TOOL', 'TOOL_RESULT', NULL, '{"session_event_id": "db1a3414-faa1-5de0-9587-a0baab72a90e", "tool": "sandbox_run_ddl", "status": "SUCCESS", "result": {"tables_created": 7, "sample_load_rows": 1000, "runtime_errors": 0}}'::jsonb, 'bfff9800-e79a-52d9-aaa9-8ef0bc33d280', '2025-11-04 09:38:15+07'::timestamptz, '2025-11-04 09:38:15+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'QUESTION', 'Sandbox chạy thành công. Trường ''so_ho_so'' nên được coi là khóa chính của fact_ho_so_luu_tru hay chỉ là khóa ngoại tới dim_benh_nhan? Vui lòng xác nhận để hoàn tất thiết kế.', NULL, '5b039e0f-ae7e-5ca3-88ba-0218aeb15834', '2025-11-04 11:20:00+07'::timestamptz, '2025-11-04 11:20:00+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'USER', 'ANSWER', 'so_ho_so nên là khóa ngoại tới dim_benh_nhan (đã ẩn danh). Khóa chính của fact nên là so_benh_an vì mỗi đợt điều trị mới sinh 1 dòng fact.', NULL, '60687b38-f36e-526c-a10d-15a268a1a0da', '2025-11-04 11:32:00+07'::timestamptz, '2025-11-04 11:32:00+07'::timestamptz),
  ('9573f767-f342-56c0-90bc-c88ff63ee157', 'AGENT', 'MESSAGE', 'Đã cập nhật thiết kế theo xác nhận của bạn. DBML đã sẵn sàng để chuyển sang HumanReview.', '{"model": "claude-sonnet-4-6"}'::jsonb, 'e166ed48-914d-5541-a0c5-45ba8af250d6', '2025-11-04 11:45:00+07'::timestamptz, '2025-11-04 11:45:00+07'::timestamptz),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0', 'USER', 'MESSAGE', 'Bổ sung thêm phân tích tỷ lệ lấp đầy Kho/Tủ/Ngăn vào mô hình hiện tại.', NULL, '9bda8727-7b6f-5a6c-82ca-8e79b17cf580', '2026-08-10 15:30:10+07'::timestamptz, '2026-08-10 15:30:10+07'::timestamptz),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0', 'AGENT', 'AGENT_CALL', NULL, '{"caller_agent": "OrchestrationAgent", "target_agent": "DWDesignAgent", "input": {"base_revision": 2, "new_analytical_requirement": "req-vimes-hs-an2"}}'::jsonb, '049ca70d-6ea9-566f-a9c3-37edd88f7a4a', '2026-08-10 15:31:00+07'::timestamptz, '2026-08-10 15:31:00+07'::timestamptz),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0', 'AGENT', 'AGENT_RESULT', NULL, '{"session_event_id": "049ca70d-6ea9-566f-a9c3-37edd88f7a4a", "agent": "DWDesignAgent", "status": "SUCCESS", "output": {"dbml_generated": true, "new_fact_tables": ["fact_ton_kho_vi_tri"]}, "llm": {"provider": "anthropic", "model": "claude-sonnet-4-6", "input_tokens": 6100, "output_tokens": 1450, "total_tokens": 7550, "temperature": 0.4, "latency_ms": 6300, "finish_reason": "end_turn"}}'::jsonb, '2c431c61-d309-5346-a097-10e9b7854955', '2026-08-10 15:36:00+07'::timestamptz, '2026-08-10 15:36:00+07'::timestamptz),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0', 'AGENT', 'MESSAGE', 'Đã tạo đề xuất thay đổi (data_model_change) với base_revision=2, đang chờ bạn Accept/Reject trong HumanReview.', '{"model": "claude-sonnet-4-6"}'::jsonb, '471c9e38-dfbe-5ac3-b927-475423c07c6b', '2026-08-10 16:20:00+07'::timestamptz, '2026-08-10 16:20:00+07'::timestamptz),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', 'USER', 'MESSAGE', 'Thiết kế DW cho phân tích rủi ro tín dụng dựa trên dữ liệu Core Banking và CRM.', NULL, 'c719c25c-effb-5382-9f22-6a17993b2738', '2025-11-08 09:00:10+07'::timestamptz, '2025-11-08 09:00:10+07'::timestamptz),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', 'AGENT', 'AGENT_CALL', NULL, '{"caller_agent": "OrchestrationAgent", "target_agent": "SourceDataAgent", "input": {"data_source_ids": ["ds-bank-core", "ds-bank-crm"]}}'::jsonb, '6d8129d9-371b-502c-8896-08b5a4767866', '2025-11-08 09:00:30+07'::timestamptz, '2025-11-08 09:00:30+07'::timestamptz),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', 'AGENT', 'AGENT_RESULT', NULL, '{"session_event_id": "6d8129d9-371b-502c-8896-08b5a4767866", "agent": "SourceDataAgent", "status": "CANCELLED", "error": "Agent execution was cancelled"}'::jsonb, 'fb4411d2-9f3c-56fc-abee-16cfdebf1413', '2025-11-08 09:05:00+07'::timestamptz, '2025-11-08 09:05:00+07'::timestamptz),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', 'USER', 'MESSAGE', 'Xin lỗi, tôi bấm nhầm huỷ. Vui lòng chạy lại phân tích nguồn dữ liệu.', NULL, '83323f96-8bca-5f73-8a68-1ca60f7e5876', '2025-11-08 09:06:00+07'::timestamptz, '2025-11-08 09:06:00+07'::timestamptz),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', 'AGENT', 'AGENT_CALL', NULL, '{"caller_agent": "OrchestrationAgent", "target_agent": "SourceDataAgent", "input": {"data_source_ids": ["ds-bank-core", "ds-bank-crm"], "retry": true}}'::jsonb, 'aff7f2b6-2314-5d19-b6dd-d813bd1ff98a', '2025-11-08 09:06:10+07'::timestamptz, '2025-11-08 09:06:10+07'::timestamptz),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', 'AGENT', 'AGENT_RESULT', NULL, '{"session_event_id": "aff7f2b6-2314-5d19-b6dd-d813bd1ff98a", "agent": "SourceDataAgent", "status": "SUCCESS", "output": {"tables_analyzed": 4, "relationships_inferred": 3}, "llm": {"provider": "anthropic", "model": "claude-sonnet-4-6", "input_tokens": 3400, "output_tokens": 700, "total_tokens": 4100, "temperature": 0.2, "latency_ms": 3900, "finish_reason": "end_turn"}}'::jsonb, 'd4b8c311-da6a-55d3-96f6-5879c3005b27', '2025-11-08 09:09:00+07'::timestamptz, '2025-11-08 09:09:00+07'::timestamptz),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a', 'AGENT', 'MESSAGE', 'Hoàn tất thiết kế DW rủi ro tín dụng phiên bản đầu tiên, đã qua Validate và Sandbox thành công.', '{"model": "claude-sonnet-4-6"}'::jsonb, 'e98051d3-fb36-57d3-87b5-f4c0e009f4bd', '2025-11-08 12:30:00+07'::timestamptz, '2025-11-08 12:30:00+07'::timestamptz),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac', 'USER', 'MESSAGE', 'Thiết kế fact bán hàng đa kênh hợp nhất từ POS và sàn TMĐT nội bộ.', NULL, '4392641e-b672-5971-9d7b-0075773e3991', '2025-11-11 09:40:05+07'::timestamptz, '2025-11-11 09:40:05+07'::timestamptz),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac', 'AGENT', 'TOOL_CALL', NULL, '{"agent": "ValidationEngine", "tool": "dbml_validate", "arguments": {"revision_candidate": 1}}'::jsonb, '64462410-dec0-5f87-8ca7-baed27c864d2', '2025-11-11 11:40:00+07'::timestamptz, '2025-11-11 11:40:00+07'::timestamptz),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac', 'TOOL', 'TOOL_RESULT', NULL, '{"session_event_id": "64462410-dec0-5f87-8ca7-baed27c864d2", "tool": "dbml_validate", "status": "SUCCESS", "result": {"syntax_ok": true, "warnings": 1}}'::jsonb, '457e4bb4-d6ff-5b12-a68f-24dc9dca80cb', '2025-11-11 11:40:05+07'::timestamptz, '2025-11-11 11:40:05+07'::timestamptz),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac', 'AGENT', 'MESSAGE', 'Thiết kế fact_doanh_thu_ban_hang đã sẵn sàng, chuyển sang HumanReview.', '{"model": "claude-sonnet-4-6"}'::jsonb, 'a03deaae-d681-5104-908a-1ec310fcb772', '2025-11-11 11:55:00+07'::timestamptz, '2025-11-11 11:55:00+07'::timestamptz);
-- ============================================================
-- 9. DATA_MODELS
-- ============================================================
INSERT INTO public.data_models (project_id, dbml, revision, id, created_at, updated_at) VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249', 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}
', 3, '334a17ab-5a72-55be-9df9-5fd337c22a6c', '2025-11-04 11:50:00+07'::timestamptz, '2026-08-10 16:20:00+07'::timestamptz),
  ('84bdeb46-0eba-564e-8437-833ede4e2718', 'Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_chan_doan {
  chan_doan_key uuid [pk]
  ten_chan_doan varchar(250)
  nhom_chan_doan varchar(100)
}

Table dim_doi_tuong {
  doi_tuong_key varchar(20) [pk]
  ten_doi_tuong varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table fact_luot_kham {
  luot_kham_key uuid [pk]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  chan_doan_key uuid [ref: > dim_chan_doan.chan_doan_key]
  doi_tuong_key varchar(20) [ref: > dim_doi_tuong.doi_tuong_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  so_luot integer
}
', 1, 'f0cfe13c-7110-5ffe-bfc6-7bd37be7e8b8', '2025-12-10 12:00:00+07'::timestamptz, '2025-12-10 12:00:00+07'::timestamptz),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae', 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
}
', 2, '669b488c-5595-518f-a10b-2d02e1561333', '2025-11-08 12:35:00+07'::timestamptz, '2026-08-05 14:10:00+07'::timestamptz),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d', 'Table dim_sku {
  sku_key varchar(30) [pk]
  category varchar(50)
  brand varchar(50)
}

Table dim_store {
  store_key varchar(10) [pk]
  region varchar(50)
  store_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  tuan integer
}

Table fact_doanh_thu_ban_hang {
  invoice_line_key uuid [pk]
  sku_key varchar(30) [ref: > dim_sku.sku_key]
  store_key varchar(10) [ref: > dim_store.store_key]
  date_key date [ref: > dim_date.date_key]
  qty integer
  revenue numeric(14,2)
  discount_amount numeric(14,2)
}
', 1, 'a42297a7-08d0-592a-b70a-8409a153ff05', '2025-11-11 11:56:00+07'::timestamptz, '2025-11-11 11:56:00+07'::timestamptz),
  ('18525676-8c6b-552b-8de7-a50899ef4b92', 'Table dim_route {
  route_key varchar(20) [pk]
  origin_hub varchar(50)
  dest_hub varchar(50)
}

Table dim_carrier {
  carrier_key varchar(20) [pk]
  carrier_name varchar(100)
  vehicle_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_shipment {
  shipment_key varchar(30) [pk]
  route_key varchar(20) [ref: > dim_route.route_key]
  carrier_key varchar(20) [ref: > dim_carrier.carrier_key]
  date_key date [ref: > dim_date.date_key]
  sla_hours integer
  actual_hours numeric(6,2)
  is_on_time boolean
}
', 2, '26d054de-06b0-51ca-86d3-270a75cc88f3', '2025-11-18 13:25:00+07'::timestamptz, '2025-11-20 09:00:00+07'::timestamptz),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277', 'Table dim_faculty {
  faculty_key varchar(10) [pk]
  faculty_name varchar(100)
}

Table dim_student {
  student_key varchar(15) [pk]
  faculty_key varchar(10) [ref: > dim_faculty.faculty_key]
  admission_year integer
}

Table fact_ket_qua_hoc_tap {
  record_key uuid [pk]
  student_key varchar(15) [ref: > dim_student.student_key]
  gpa numeric(3,2)
  graduation_status varchar(20)
}
', 1, '2cc82e1c-0bd2-53bf-9574-29360fa77708', '2025-12-02 10:45:00+07'::timestamptz, '2025-12-02 10:45:00+07'::timestamptz),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48', 'Table dim_line {
  line_key varchar(10) [pk]
  line_name varchar(50)
}

Table dim_shift {
  shift_key varchar(5) [pk]
  shift_name varchar(30)
}

Table fact_production {
  event_key bigint [pk]
  line_key varchar(10) [ref: > dim_line.line_key]
  shift_key varchar(5) [ref: > dim_shift.shift_key]
  planned_units integer
  produced_units integer
  defect_units integer
  downtime_minutes integer
  availability numeric(5,4)
  performance numeric(5,4)
  quality numeric(5,4)
  oee numeric(5,4)
}
', 1, '353a2d9e-ab98-5c99-b541-5a168aa5b332', '2025-12-08 15:50:00+07'::timestamptz, '2025-12-08 15:50:00+07'::timestamptz),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594', 'Table dim_product {
  product_key varchar(10) [pk]
  product_name varchar(100)
}

Table dim_policy {
  policy_key varchar(20) [pk]
  product_key varchar(10) [ref: > dim_product.product_key]
}

Table fact_claim {
  claim_key varchar(20) [pk]
  policy_key varchar(20) [ref: > dim_policy.policy_key]
  claim_amount numeric(18,2)
  claim_status varchar(20)
  is_suspected_fraud boolean
}
', 1, '393a9c32-6723-514e-84bc-d6fa875157bf', '2025-10-20 09:00:00+07'::timestamptz, '2025-10-20 09:00:00+07'::timestamptz),
  ('f8c4432f-0252-5275-a581-958039b98639', 'Table dim_subscriber {
  subscriber_key varchar(15) [pk]
  plan_key varchar(10)
  region varchar(30)
  status varchar(15)
}

Table dim_plan {
  plan_key varchar(10) [pk]
  plan_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_usage_monthly {
  usage_key uuid [pk]
  subscriber_key varchar(15) [ref: > dim_subscriber.subscriber_key]
  date_key date [ref: > dim_date.date_key]
  total_data_mb numeric(14,2)
  total_voice_minutes numeric(12,2)
  arpu numeric(12,2)
  is_churned boolean
}
', 2, 'c68e1dd1-f2d4-50bd-bd34-9743e6d79968', '2025-12-15 12:20:00+07'::timestamptz, '2025-12-18 09:00:00+07'::timestamptz),
  ('6268eced-f86b-5e52-b0a9-262a806879e9', 'Table dim_category {
  category_key varchar(30) [pk]
  category_name varchar(100)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table fact_cart_funnel {
  event_key uuid [pk]
  category_key varchar(30) [ref: > dim_category.category_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  add_to_cart_count integer
  checkout_count integer
  purchase_count integer
}

Table fact_ad_spend {
  campaign_key varchar(20) [pk]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  spend numeric(14,2)
  conversions integer
}
', 1, '97998605-51ac-53da-8391-89e07a426729', '2026-01-05 13:05:00+07'::timestamptz, '2026-01-05 13:05:00+07'::timestamptz);

-- ============================================================
-- 10. DATA_MODEL_CHANGES
-- ============================================================
INSERT INTO public.data_model_changes (data_model_id, base_revision, proposed_dbml, status, user_id, id, created_at, updated_at) VALUES
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c', 1, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  // v2: bổ sung so_ngay_den_khi_luu_tru
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}
', 'ACCEPTED', '15c1be82-ea36-5205-af17-7fb5947c2027', '22906d5d-30f7-59bc-abf1-2ddb3c25dc04', '2025-11-04 14:00:00+07'::timestamptz, '2025-11-04 15:30:00+07'::timestamptz),
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c', 2, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}

// v3: bổ sung fact_ton_kho_vi_tri cho phân tích tỷ lệ lấp đầy
Table fact_ton_kho_vi_tri {
  snapshot_key uuid [pk]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  ngay_key date [ref: > dim_date.date_key]
  so_ho_so_hien_co integer
  ty_le_lap_day numeric(5,4)
}
', 'ACCEPTED', 'a678ac27-3077-5ef2-8919-5218b2e48791', 'b276cfe5-c34e-56f4-b56d-7fd4ed51f1fc', '2026-08-10 15:36:10+07'::timestamptz, '2026-08-10 16:20:00+07'::timestamptz),
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c', 2, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
  // đề xuất song song: thêm truong_thanh_toan
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}
', 'REJECTED', 'e892c55a-77c6-5c8f-8e00-00da20839ba9', '8a59b785-2998-5116-81ab-90ae43f6667d', '2025-11-05 09:00:00+07'::timestamptz, '2025-11-05 10:15:00+07'::timestamptz),
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c', 3, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}

// v4 (đang chờ duyệt): thêm dim_bac_si phục vụ phân tích theo bác sĩ phụ trách
Table dim_bac_si {
  bac_si_key uuid [pk]
  ten_bac_si_hash varchar(64)
  khoa_key varchar(10) [ref: > dim_khoa.khoa_key]
}
', 'PROPOSED', 'a678ac27-3077-5ef2-8919-5218b2e48791', '15ceb42f-f3ad-5acd-a797-7fdb686272f0', '2026-08-11 08:30:00+07'::timestamptz, '2026-08-11 08:30:00+07'::timestamptz),
  ('f0cfe13c-7110-5ffe-bfc6-7bd37be7e8b8', 1, 'Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_chan_doan {
  chan_doan_key uuid [pk]
  ten_chan_doan varchar(250)
  nhom_chan_doan varchar(100)
}

Table dim_doi_tuong {
  doi_tuong_key varchar(20) [pk]
  ten_doi_tuong varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table fact_luot_kham {
  luot_kham_key uuid [pk]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  chan_doan_key uuid [ref: > dim_chan_doan.chan_doan_key]
  doi_tuong_key varchar(20) [ref: > dim_doi_tuong.doi_tuong_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  so_luot integer
}

// đề xuất: thêm dim_bac_si_chan_doan
', 'PROPOSED', '4c507932-ae90-57a1-8765-885e45eba112', 'e7131a5f-c437-5bea-917d-711990125d77', '2025-12-11 09:00:00+07'::timestamptz, '2025-12-11 09:00:00+07'::timestamptz),
  ('669b488c-5595-518f-a10b-2d02e1561333', 1, 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
  fraud_score numeric(5,4) // v2: thêm điểm rủi ro gian lận
}
', 'ACCEPTED', '0740e12f-bc1c-556f-9cc7-3ec5332e692e', '5c975d54-8385-5f7f-91d0-48ccf5806f67', '2025-11-08 13:00:00+07'::timestamptz, '2025-11-08 14:00:00+07'::timestamptz),
  ('669b488c-5595-518f-a10b-2d02e1561333', 1, 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  credit_limit numeric(18,2) // đề xuất dựa trên revision cũ
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
}
', 'CONFLICTED', '187ebbb4-aff9-555e-93e8-84718180c565', '1ccf808f-beaf-5193-91b6-6a216432b7ca', '2025-11-08 13:10:00+07'::timestamptz, '2025-11-08 14:05:00+07'::timestamptz),
  ('a42297a7-08d0-592a-b70a-8409a153ff05', 1, 'Table dim_sku {
  sku_key varchar(30) [pk]
  category varchar(50)
  brand varchar(50)
}

Table dim_store {
  store_key varchar(10) [pk]
  region varchar(50)
  store_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  tuan integer
}

Table fact_doanh_thu_ban_hang {
  invoice_line_key uuid [pk]
  sku_key varchar(30) [ref: > dim_sku.sku_key]
  store_key varchar(10) [ref: > dim_store.store_key]
  date_key date [ref: > dim_date.date_key]
  qty integer
  revenue numeric(14,2)
  discount_amount numeric(14,2)
  promo_code varchar(20) // đề xuất bổ sung mã khuyến mãi
}
', 'REJECTED', '25a6f954-f1cd-567d-88a0-630c4407b254', '91e373e7-f5a4-519a-8743-c6c10e9c6c65', '2025-11-12 09:00:00+07'::timestamptz, '2025-11-12 10:30:00+07'::timestamptz),
  ('26d054de-06b0-51ca-86d3-270a75cc88f3', 1, 'Table dim_route {
  route_key varchar(20) [pk]
  origin_hub varchar(50)
  dest_hub varchar(50)
}

Table dim_carrier {
  carrier_key varchar(20) [pk]
  carrier_name varchar(100)
  vehicle_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_shipment {
  shipment_key varchar(30) [pk]
  route_key varchar(20) [ref: > dim_route.route_key]
  carrier_key varchar(20) [ref: > dim_carrier.carrier_key]
  date_key date [ref: > dim_date.date_key]
  sla_hours integer
  actual_hours numeric(6,2)
  is_on_time boolean
  delay_minutes integer // v2: thêm số phút trễ
}
', 'ACCEPTED', '85651d6b-4cc0-56ba-ba15-ffc404f10abc', 'f649588b-edb9-52ed-8fc1-f3fc8be59bb4', '2025-11-19 08:00:00+07'::timestamptz, '2025-11-20 09:00:00+07'::timestamptz),
  ('2cc82e1c-0bd2-53bf-9574-29360fa77708', 1, 'Table dim_faculty {
  faculty_key varchar(10) [pk]
  faculty_name varchar(100)
}

Table dim_student {
  student_key varchar(15) [pk]
  faculty_key varchar(10) [ref: > dim_faculty.faculty_key]
  admission_year integer
}

Table fact_ket_qua_hoc_tap {
  record_key uuid [pk]
  student_key varchar(15) [ref: > dim_student.student_key]
  gpa numeric(3,2)
  graduation_status varchar(20)
}

// đề xuất: thêm fact_hoc_phi
', 'PROPOSED', '729525be-38aa-50fd-8ea9-3fedf76615f1', '9cbd88d1-47f2-5740-a897-5f366032338d', '2025-12-03 10:00:00+07'::timestamptz, '2025-12-03 10:00:00+07'::timestamptz),
  ('353a2d9e-ab98-5c99-b541-5a168aa5b332', 1, 'Table dim_line {
  line_key varchar(10) [pk]
  line_name varchar(50)
}

Table dim_shift {
  shift_key varchar(5) [pk]
  shift_name varchar(30)
}

Table fact_production {
  event_key bigint [pk]
  line_key varchar(10) [ref: > dim_line.line_key]
  shift_key varchar(5) [ref: > dim_shift.shift_key]
  planned_units integer
  produced_units integer
  defect_units integer
  downtime_minutes integer
  availability numeric(5,4)
  performance numeric(5,4)
  quality numeric(5,4)
  oee numeric(5,4)
  target_oee numeric(5,4) // đề xuất thêm mục tiêu OEE để so sánh
}
', 'PROPOSED', 'c0445430-562e-5472-bea6-06f3a5d6f645', 'd7b57f42-cbef-55b3-a758-18d52334387e', '2025-12-09 09:00:00+07'::timestamptz, '2025-12-09 09:00:00+07'::timestamptz),
  ('c68e1dd1-f2d4-50bd-bd34-9743e6d79968', 1, 'Table dim_subscriber {
  subscriber_key varchar(15) [pk]
  plan_key varchar(10)
  region varchar(30)
  status varchar(15)
}

Table dim_plan {
  plan_key varchar(10) [pk]
  plan_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_usage_monthly {
  usage_key uuid [pk]
  subscriber_key varchar(15) [ref: > dim_subscriber.subscriber_key]
  date_key date [ref: > dim_date.date_key]
  total_data_mb numeric(14,2)
  total_voice_minutes numeric(12,2)
  arpu numeric(12,2)
  is_churned boolean
  churn_risk_score numeric(5,4) // v2: bổ sung điểm dự báo rời mạng
}
', 'ACCEPTED', 'e892c55a-77c6-5c8f-8e00-00da20839ba9', '685f57f6-e920-5c1d-bcd0-abfb9653882d', '2025-12-16 08:00:00+07'::timestamptz, '2025-12-18 09:00:00+07'::timestamptz),
  ('97998605-51ac-53da-8391-89e07a426729', 1, 'Table dim_category {
  category_key varchar(30) [pk]
  category_name varchar(100)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table fact_cart_funnel {
  event_key uuid [pk]
  category_key varchar(30) [ref: > dim_category.category_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  add_to_cart_count integer
  checkout_count integer
  purchase_count integer
}

Table fact_ad_spend {
  campaign_key varchar(20) [pk]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  spend numeric(14,2)
  conversions integer
}

// đề xuất: thêm fact_customer_ltv
', 'PROPOSED', '4c507932-ae90-57a1-8765-885e45eba112', '8a1746e4-8593-5ec7-b20c-4fa94ceb1032', '2026-01-06 11:00:00+07'::timestamptz, '2026-01-06 11:00:00+07'::timestamptz);
COMMIT;