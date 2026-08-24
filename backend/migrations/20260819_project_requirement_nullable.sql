-- Project có thể được tạo trước khi người dùng nhập yêu cầu nghiệp vụ thô.
ALTER TABLE projects
    ALTER COLUMN requirement DROP NOT NULL;
