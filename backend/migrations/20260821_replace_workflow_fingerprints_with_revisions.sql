ALTER TABLE projects
    ADD COLUMN requirement_revision INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN source_revision INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN analyzed_requirement_revision INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN analyzed_source_revision INTEGER NOT NULL DEFAULT 0;

UPDATE projects
SET requirement_revision = 1
WHERE requirement IS NOT NULL AND BTRIM(requirement) <> '';

UPDATE projects AS project
SET source_revision = 1
WHERE EXISTS (
    SELECT 1 FROM data_sources AS source WHERE source.project_id = project.id
);

ALTER TABLE data_models
    ADD COLUMN generated_from_requirement_revision INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN generated_from_source_revision INTEGER NOT NULL DEFAULT 1;

ALTER TABLE projects
    DROP COLUMN IF EXISTS requirement_analysis_fingerprint,
    DROP COLUMN IF EXISTS analytical_analysis_fingerprint;

ALTER TABLE data_models DROP COLUMN IF EXISTS input_fingerprint;
ALTER TABLE data_model_changes DROP COLUMN IF EXISTS input_fingerprint;
