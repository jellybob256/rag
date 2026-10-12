## Problem

People often need answers from reference material, but reading through long documents is slow and inefficient.

## Goal

Build an API that allows users to ask natural language questions and get accurate answers from a set of documents. Answers should cite the source documents.

## Dataset

Generic reference documents on topics such as programming, AI, and space exploration. Stored in `data/` folder.

## Non-Goals

- Real company data
- Real-time updates
- Large-scale user traffic

## Constraints

- Latency < 3 seconds
- Cost < $0.01 per request
- Answers must cite sources