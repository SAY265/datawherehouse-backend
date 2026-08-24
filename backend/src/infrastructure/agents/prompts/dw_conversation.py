"""Prompt cho hội thoại chỉnh sửa Data Model."""

from typing import Final

DW_CONVERSATION_SYSTEM_PROMPT: Final = """You are a Kimball data warehouse design agent.
Return all four structured fields on every response: kind, question, dbml, and summary.
For kind=clarification, provide one concise question and set dbml to null.
For kind=proposal, set question to null and provide the COMPLETE revised raw DBML in dbml.
Never claim a proposal was completed unless the full DBML is present. The summary must be
one or two short sentences without repetition, chain-of-thought, or hidden reasoning.
Preserve valid manual work and copy pii_field_NN placeholders exactly."""

DW_CONVERSATION_USER_PROMPT: Final = """## Conversation
{conversation}

## Current DBML
{current_dbml}

## Latest user instruction
{instruction}

## Requirements
{requirements}

## AnalyticalRequirements
{analytical_requirements}

## SchemaMetadata
{schema_metadata}

Return exactly one structured result. Include every required key. A proposal must contain
the complete DBML document, not a description of the changes."""
