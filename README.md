# Campus Customs — Homework 4

A React/Vite/TypeScript Yale merchandise storefront with a FastAPI/PydanticAI shopping assistant.

## Run locally

1. Put the supplied `campus_customs.db` at `/Users/iin3rdyii/Desktop/data/campus_customs.db` (the database and environment file are intentionally excluded from this public package).
2. Put the Portkey key in the parent `.env` as `PORTKEY_API_KEY`.
3. Run `./run_local.sh`.
4. Open `http://localhost:8000/`.

The QA walkthrough is available at `/app_check.html` after the frontend build is copied into `backend/static`.

## Project areas

- `src/`: React storefront, product cards, cart, detail modal, account UI, and chat widget.
- `backend/`: FastAPI app, PydanticAI agent, local SQLite tools, typed models, prompts, and security controls.
- `output/`: harness, design, usability, QA, and assignment documentation.

Never commit `.env`, API keys, user data, or the Campus Customs database.
