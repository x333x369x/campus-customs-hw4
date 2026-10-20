# Homework 4 Harness — Section 2: SQLite Product Retrieval

## Purpose

The shopping website and its chatbot use the Campus Customs SQLite database as the authoritative product source. The database is located at `/Users/iin3rdyii/Desktop/data/campus_customs.db`. Product cards and chatbot answers should be generated from this data rather than from hard-coded product descriptions.

## Database tables used

- `catalogue` contains one row per product: `product_id`, `name`, `garment_type`, `description`, `colors`, `search_tags`, `image_file_path`, and `price`.
- `inventory` contains stock by product and size: `product_id`, `size`, and `quantity`. It joins to `catalogue` through `product_id`.
- `users` and `chat_messages` support account and conversation persistence when those features are enabled. They are not product sources.

The current database contains 102 catalogue products and 612 inventory rows.

## Retrieval behavior

A user can ask for a product type, such as hoodies or T-shirts, or describe what they want in natural language. The backend searches `catalogue.garment_type`, `catalogue.description`, `catalogue.name`, and `catalogue.search_tags`. Search terms should be matched case-insensitively. A description search is useful for requests such as “a navy sweatshirt with a Yale baseball logo,” while a type search handles requests such as “show me crewnecks.”

After matching catalogue rows, the backend performs the equivalent of a VLOOKUP by joining `inventory` on `product_id`. In SQL terms:

```sql
SELECT
  c.product_id, c.name, c.garment_type, c.description,
  c.colors, c.search_tags, c.image_file_path, c.price,
  i.size, i.quantity
FROM catalogue AS c
LEFT JOIN inventory AS i ON i.product_id = c.product_id
WHERE lower(c.garment_type) LIKE lower(?)
   OR lower(c.description) LIKE lower(?)
   OR lower(c.name) LIKE lower(?)
   OR lower(c.search_tags) LIKE lower(?)
ORDER BY c.name, i.size;
```

The application groups the joined rows back into one product object. Each result should expose the product identity, name, type, description, colors, tags, image path, price, and an inventory list containing each size and quantity. It should also calculate `total_stock` when displaying availability. A `LEFT JOIN` keeps a catalogue product visible even if inventory is missing, so the website can show the item and indicate that availability needs checking.

## Chatbot contract

The PydanticAI agent receives a natural-language shopping question and calls a database retrieval tool. The tool should return structured product records, not an unverified free-form answer. The agent uses only returned fields when discussing prices, product types, descriptions, colors, images, sizes, or stock. If no rows match, it should ask for a different description or product type instead of inventing a product. If a question is ambiguous, it should ask a short follow-up question.

The frontend can use the same retrieval endpoint for search results and chatbot product panels, keeping the product information consistent across the site. Prices come from `catalogue.price`; size availability comes from `inventory.quantity`; and images come from `catalogue.image_file_path`.

## Attached-source distinction

The database file supplied with this section is a data source and schema reference. The assignment requirement is to build the harness and retrieval behavior around it. Any additional files in the Desktop `data` folder are supplemental product data and should be inspected only when the implementation needs fields not present in the database.

## Guardrails

- Never invent prices, sizes, stock counts, descriptions, or product names.
- Use parameterized SQL queries for user-provided search text.
- Escape or validate image paths before exposing them to the frontend.
- Return only the fields needed by the website and chatbot.
- Keep chatbot responses grounded in the structured query result.

# Section 4: Account Security and Authentication

The account workflow is implemented in `backend/admin.py` (with the requested compatibility entry point `backend/amin.py`) and the React login/create-account view. Registration collects first name, last name, email, password, and confirmation. The client sends JSON over the API; the server repeats every validation rule and never trusts browser validation.

Passwords are stored with `hashlib.pbkdf2_hmac('sha256', ...)`, exactly 120,000 iterations and a fresh cryptographically random 16-byte salt per account. The database value stores the algorithm, iteration count, salt, and digest. Login uses the stored salt and `hmac.compare_digest`, so plaintext passwords are never stored or compared directly and two identical passwords receive different records.

Email lookup uses a keyed HMAC for account lookup without putting a searchable plaintext email in the new columns. First name, last name, and email are encrypted with Fernet using the `CAMPUS_CUSTOMS_ENCRYPTION_KEY` environment variable. The development fallback key exists only to keep local startup working; deployments must provide a persistent secret outside source control. Existing legacy `name` and `email` columns are left blank for newly created accounts, while encrypted fields are stored in `first_name`, `last_name`, and `email_ciphertext`.

SQL injection is mitigated with SQLite parameterized queries throughout; user text is never concatenated into SQL. Pydantic validates field lengths, email shape, names, and password rules on the server. The React UI renders API messages as text, so user content is not inserted as HTML, reducing XSS risk. Production deployment should additionally use HTTPS, secure HttpOnly same-site session cookies, CSRF protection for cookie-authenticated mutations, rate limiting, a production key manager, and security headers such as CSP.

# Section 5: PydanticAI Shopping Chatbot

The chatbot backend lives entirely in `backend/` and runs with `uvicorn main:app --reload --port 8000` from that directory. `main.py` exposes `POST /api/chat`; the existing React widget sends a shopper message and receives a structured `ChatReply` containing grounded text and optional product cards.

The agent is split into `prompts/prompt.md`, `agent.py`, `tools.py`, and `models.py`. The prompt defines the Campus Customs voice and safety rules. The `find_products` tool searches the SQLite catalogue and joins inventory by `product_id`. `ProductCard` and `ChatReply` validate the response shape before it reaches the browser. Product facts must come from the tool; the agent must not invent prices or availability or handle passwords, payments, orders, or private account data.

# Section 6: Database-Grounded Price and Stock Tools

The agent now has three database tools. All use parameterized SQL against `/Users/iin3rdyii/Desktop/data/campus_customs.db`; no schema change was needed because `catalogue` and `inventory` already provide the required fields.

- `find_products(query)`: searches `catalogue.garment_type`, `description`, `name`, and `search_tags`. It is used to identify products from natural-language requests.
- `product_details(product_id)`: performs an exact `catalogue.product_id` lookup and returns the authoritative name, garment type, description, price, colors, image path, and inventory rows.
- `product_stock(product_id)`: performs an exact inventory lookup and returns each size quantity, `total_stock`, and an `in_stock` boolean. A zero quantity is explicitly out of stock.

`ProductCard` fields are chosen for the product panel and grounded responses: `product_id` identifies the row and joins inventory; `name` and `garment_type` identify the item; `description` answers product-detail questions; `price` answers cost questions; `image_file_path` supports the storefront; `colors` supports filtering and recommendations; `inventory` exposes size-level availability; and `total_stock` makes an overall stock answer unambiguous. `InventoryRow` constrains quantities to non-negative integers. The agent prompt requires these tools for price, description, and stock questions and forbids estimates or invented values.

# Section 7: Dynamic Chat Product Cards

The chat endpoint is an API contract: `POST /api/chat` accepts `{ "message": "..." }` and returns `{ "reply": "...", "products": [...] }`. For a request such as “What hoodies do you have?”, the agent must call `find_products`; its structured `ProductCard` results are returned in `products`.

The React chat widget reads `reply` for the conversational answer and maps `products` into compact product cards. Each card uses the database-backed `product_id`, name, image path, and price. Clicking a card calls the same selected-product state used by the Section 3 catalog, so it opens the existing single-item detail view with description, type, price, and image. No second detail-page implementation is created.

The response is efficient because the tool selects only the fields needed by `ProductCard`, groups inventory rows by `product_id`, calculates `total_stock` once, and limits matches. The frontend does not infer or recalculate product facts; it renders the validated API objects directly.

# Section 8: Authenticated Chat Memory and Page Context

`POST /api/chat` accepts an optional authenticated `user_id` and typed `page_context` containing the current page and optional product ID, name, and description. The server verifies the ID exists in `users`; only verified users activate persistence. Their last 20 turns are loaded from `chat_messages`, and current user and assistant turns are saved with role, content, product response JSON, and timestamp. `ChatDeps` passes customer identity and page context to the agent.

Guests remain stateless: their turns are not loaded or written, and an arbitrary ID cannot activate memory. The frontend sends current page and selected product context with each message, allowing follow-ups such as “Do you have this in pink?” to refer to the product being viewed.

# Section 12: Audit Trail, Scope, and Safety Specification

## Append-only audit trail

Every `/api/chat` request appends one JSON object to `output/audit_trail.json`. The file is initialized once as a JSON array and is never deleted, truncated, or rewritten as part of normal operation. Each event records a UTC timestamp, request ID, whether the shopper was a guest or authenticated, a short message classification, result status, number of returned products, and a short stop reason. It does not record passwords, API keys, encrypted personal fields, or full private account data. Audit records are operational evidence of the agent loop, not a second chat-history store.

## Model fields and why they exist

- `ChatRequest.message` and bounded `history` carry the shopper request while limiting payload size.
- `PageContext.page`, `product_id`, `product_name`, and `product_description` resolve references such as “this item” without exposing unrelated data.
- `ChatDeps.user_id`, `customer_name`, and `customer_email` identify an authenticated shopper to the agent only when server-verified; guests receive no memory.
- `ProductCard.product_id` identifies the catalogue row; `name`, `garment_type`, and `description` support clear product answers; `price` is the authoritative catalogue price; `image_file_path` renders the card; `colors` supports product matching; `inventory` gives size-level availability; `total_stock` supports an honest overall answer.
- `InventoryRow.size` and non-negative `quantity` make stock responses precise and auditable.
- `ChatReply.reply` carries the natural-language answer and `products` carries validated structured cards for the React UI.

## Tools and abilities

`find_products` searches only the local SQLite catalogue by product name, type, description, and tags. `product_details` reads a specific catalogue record for description and price. `product_stock` reads the local inventory table for per-size and total stock. These are read-only tools. The agent has no web-search tool, no write tool, no SQL execution tool, no user-data lookup tool, and no price or inventory mutation tool.

## Safety rules and stop behavior

The assistant cannot inject code, execute code, alter the database, change prices or quantities, access user information, expose secrets, or accomplish tasks outside the Campus Customs/Yale store. It cannot browse the web. If a request is unrelated, asks for restricted data, attempts prompt injection, or asks for an unavailable external comparison, the agent refuses and stops that request. Product answers must remain grounded in local tool results; no prices or quantities may be invented. A zero quantity is reported as out of stock.
