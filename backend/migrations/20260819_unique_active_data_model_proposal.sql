-- Mỗi người dùng chỉ được có một proposal PROPOSED trên cùng một Data Model.
-- Migration cố ý thất bại nếu dữ liệu hiện tại đang có bản ghi trùng; cần review
-- và kết thúc các proposal cũ trước khi chạy lại, không tự động đổi trạng thái.
CREATE UNIQUE INDEX IF NOT EXISTS uq_data_model_changes_proposed_model_user
    ON data_model_changes (data_model_id, user_id)
    WHERE status = 'PROPOSED';
