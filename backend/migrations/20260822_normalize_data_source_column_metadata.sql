-- Chuẩn hóa SchemaMetadata JSONB sang contract column/constraint có cấu trúc.
-- Migration cố ý thất bại nếu foreign_key_reference cũ không có dạng table.column.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM data_sources AS source,
             jsonb_array_elements(
                 CASE WHEN jsonb_typeof(source.schema_metadata->'tables') = 'array'
                     THEN source.schema_metadata->'tables'
                     ELSE '[]'::jsonb
                 END
             ) AS table_item,
             jsonb_array_elements(
                 CASE WHEN jsonb_typeof(table_item->'columns') = 'array'
                     THEN table_item->'columns'
                     ELSE '[]'::jsonb
                 END
             ) AS column_item
        WHERE column_item ? 'foreign_key_reference'
          AND column_item->>'foreign_key_reference' IS NOT NULL
          AND column_item->>'foreign_key_reference' !~ '^.+\.[^.]+$'
    ) THEN
        RAISE EXCEPTION 'Invalid legacy foreign_key_reference in data_sources.schema_metadata';
    END IF;
END $$;

UPDATE data_sources AS source
SET schema_metadata = jsonb_set(
    source.schema_metadata,
    '{tables}',
    COALESCE(
        (
            SELECT jsonb_agg(
                table_item || jsonb_build_object(
                    'columns',
                    COALESCE(
                        (
                            SELECT jsonb_agg(
                                (
                                    column_item
                                    - 'semantic_type'
                                    - 'sample_values'
                                    - 'options'
                                    - 'unique'
                                    - 'foreign_key_reference'
                                    - 'default_value'
                                    - 'constraints'
                                ) || jsonb_build_object(
                                    'data_type', CASE
                                        WHEN column_item->>'data_type' = 'OPTION'
                                          OR column_item->>'semantic_type' = 'CATEGORY'
                                            THEN 'CATEGORY'
                                        WHEN UPPER(column_item->>'data_type') IN ('INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT')
                                            THEN 'INTEGER'
                                        WHEN UPPER(column_item->>'data_type') IN ('FLOAT', 'DOUBLE', 'REAL')
                                            THEN 'NUMBER'
                                        WHEN UPPER(column_item->>'data_type') IN ('DECIMAL', 'NUMERIC')
                                            THEN 'DECIMAL'
                                        WHEN UPPER(column_item->>'data_type') LIKE 'TIMESTAMP%'
                                            THEN 'DATETIME'
                                        WHEN UPPER(column_item->>'data_type') LIKE 'TIME%'
                                            THEN 'TIME'
                                        WHEN UPPER(column_item->>'data_type') IN ('DATE', 'BOOLEAN')
                                            THEN UPPER(column_item->>'data_type')
                                        ELSE 'TEXT'
                                    END,

                                    'distinct_values', CASE
                                        WHEN jsonb_typeof(column_item->'distinct_values') = 'array'
                                          AND jsonb_array_length(column_item->'distinct_values') > 0
                                            THEN column_item->'distinct_values'
                                        WHEN jsonb_typeof(column_item->'options') = 'array'
                                            THEN column_item->'options'
                                        ELSE '[]'::jsonb
                                    END,
                                    'constraints',
                                        COALESCE(
                                            (
                                                SELECT jsonb_agg(
                                                    CASE
                                                        WHEN jsonb_typeof(constraint_item) = 'string'
                                                            THEN jsonb_build_object(
                                                                'type', 'CHECK',
                                                                'expression', constraint_item #>> '{}'
                                                            )
                                                        ELSE constraint_item
                                                    END
                                                )
                                                FROM jsonb_array_elements(
                                                    CASE
                                                        WHEN jsonb_typeof(column_item->'constraints') = 'array'
                                                            THEN column_item->'constraints'
                                                        ELSE '[]'::jsonb
                                                    END
                                                ) AS constraint_item
                                            ),
                                            '[]'::jsonb
                                        )
                                        || CASE WHEN COALESCE((column_item->>'unique')::boolean, false)
                                            THEN jsonb_build_array(jsonb_build_object('type', 'UNIQUE'))
                                            ELSE '[]'::jsonb END
                                        || CASE WHEN column_item->>'foreign_key_reference' IS NOT NULL
                                            THEN jsonb_build_array(jsonb_build_object(
                                                'type', 'FOREIGN_KEY',
                                                'reference_table', regexp_replace(
                                                    column_item->>'foreign_key_reference',
                                                    '\.[^.]+$',
                                                    ''
                                                ),
                                                'reference_column', regexp_replace(
                                                    column_item->>'foreign_key_reference',
                                                    '^.*\.',
                                                    ''
                                                )
                                            ))
                                            ELSE '[]'::jsonb END
                                        || CASE WHEN column_item->'default_value' IS NOT NULL
                                            AND column_item->'default_value' <> 'null'::jsonb
                                            THEN jsonb_build_array(jsonb_build_object(
                                                'type', 'DEFAULT',
                                                'value', column_item->'default_value'
                                            ))
                                            ELSE '[]'::jsonb END
                                )
                            )
                            FROM jsonb_array_elements(
                                CASE WHEN jsonb_typeof(table_item->'columns') = 'array'
                                    THEN table_item->'columns'
                                    ELSE '[]'::jsonb
                                END
                            ) AS column_item
                        ),
                        '[]'::jsonb
                    )
                )
            )
            FROM jsonb_array_elements(
                CASE WHEN jsonb_typeof(source.schema_metadata->'tables') = 'array'
                    THEN source.schema_metadata->'tables'
                    ELSE '[]'::jsonb
                END
            ) AS table_item
        ),
        '[]'::jsonb
    )
)
WHERE source.schema_metadata IS NOT NULL;
