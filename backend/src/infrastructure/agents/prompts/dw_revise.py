"""Prompt cho update và prompt revision của DWDesignAgent."""

from typing import Final

DW_REVISE_SYSTEM_PROMPT: Final = """You are a Kimball data warehouse designer.
Return the COMPLETE revised raw DBML in the dbml field.
Preserve valid manual work and apply the requested or input-driven changes.
Ground the result in every supplied Requirement, AnalyticalRequirement and SchemaMetadata.
Declare each relationship once and copy pii_field_NN placeholders exactly."""

DW_REVISE_USER_PROMPT: Final = """## Current DBML
{current_dbml}

## User instruction
{instruction}

## Requirements
{requirements}

## AnalyticalRequirements
{analytical_requirements}

## SchemaMetadata
{schema_metadata}

## Validation issues
{validation_issues}

Return the complete revised DBML."""
