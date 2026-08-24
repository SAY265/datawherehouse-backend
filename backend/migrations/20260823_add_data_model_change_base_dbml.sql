ALTER TABLE data_model_changes
ADD COLUMN IF NOT EXISTS base_dbml TEXT;

UPDATE data_model_changes AS changes
SET base_dbml = models.dbml
FROM data_models AS models
WHERE changes.data_model_id = models.id
  AND changes.base_dbml IS NULL;

ALTER TABLE data_model_changes
ALTER COLUMN base_dbml SET NOT NULL;
