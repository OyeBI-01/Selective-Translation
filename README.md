# Selective-Translation with Entity Preservation

## Overview

This project implements a Selective Translation system that translates text while preserving certain entities (proper nouns, technical terms, and titles). The system ensures that important terms remain unchanged during translation.

## How It Works

1. Extract Named Entities: Identifies entities (such as proper nouns and dates) using an LLM-based approach.

2. Mask Entities: Replaces detected entities with placeholders.

3. Translate the Text: Translates the masked text while keeping entities unchanged.

4. Restore Entities: Replaces placeholders with the original entities to produce the final translated output.
