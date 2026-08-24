-- Trạng thái cấu hình là application-derived contract, không phải persistence state.
ALTER TABLE sandbox_configs
    DROP COLUMN IF EXISTS status;
