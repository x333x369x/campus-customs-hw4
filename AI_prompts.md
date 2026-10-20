
# Prompt log

## Receipt extraction

File: `prompts/receipts_extract.md`

Purpose: extract one structured JSON row from each purchase receipt PDF before matching transactions to bank and credit-card lines.

## Bank statement extraction

File: `prompts/bank_extract.md`

Purpose: extract and classify each individual January bank-statement transaction before reconciliation with receipts and credit-card activity.

## Credit-card charge extraction

File: `prompts/card_extract.md`

Purpose: extract and classify each January credit-card charge before reconciliation with bank transactions and receipts.

## Reconciliation and income-statement decisions

File: `prompts/reconcile.md`

Purpose: match duplicate and split amounts, resolve mixed business/personal transactions, exclude non-January activity, and decide the single January income-statement amount for each logged item.

---

# Section 2: ZeroEyes Seller Brief

## Prompt 1

Create a file called `assets/seller_brief.md`. In it, document that we are building an agent to help ZeroEyes find other business customers and draft outreach emails. The agent must not send emails. Include the company selected, the reason for selecting it, ZeroEyes’ customer-facing websites, and the plan to compare current deployment locations with continental U.S. regions where ZeroEyes is not deployed in order to create outreach for those areas.

## Prompt 2

This is Section 2, so add the prompts used to `AI_prompts.md`.

---

# Section 4: Company Profile Agent

## Prompt 1

Build one PydanticAI agent in `sales_agent.py` that loads `prompts/sales_agent.md` as its system prompt. Give it the tools needed to create a company profile from a natural-language query. For ZeroEyes, research only relevant, sourceable information that supports prospecting and outreach, avoiding unrelated material to reduce token use. Do not invent facts. Run the agent, save its agent-loop interactions to `output/audit_log.json`, and save the detailed company profile to `assets/company_profile.json`. Reuse work from previous sections instead of duplicating it.

Use this command structure:

```bash
python sales_agent.py "Build a profile of this company." --url https://www.company_url.com
```

---

# Section 5: Customer Targets and Draft Outreach

## Prompt 1

Update the existing `prompts/sales_agent.md` instructions so the single PydanticAI agent can read the ZeroEyes company profile, search the web for suitable prospective customer companies, inspect each candidate's website for relevant and sourceable business intelligence, and draft a targeted email for each prospect. Do not send any emails and do not invent company facts or contact email addresses. Find exactly three customer targets, save company information and verified public contact details to `outputs/targets.json`, save the unsent email drafts to `output/emails.json`, and continue updating `output/audit_log.json` with the agent-loop interactions. Reuse existing work rather than duplicating it.

Use this command structure:

```bash
python sales_agent.py "Find 3 good customer targets for this company and draft outreach emails." --profile assets/company_profile.json
```

---

# Section 6: Agent Harness Summary

## Prompt 1

Create `HARNESS.md` at the project root. Write a short, human-readable, non-technical summary of how parameters and instructions are provided to the agent. Include the tools, packages, and agents created for the project. Explain the stopping rules and guardrails, especially that the agent must never send emails and that all results and drafts must be reviewed by a person before external use.

---

# Section 7: Reflection

## Prompt 1

Create `output/reflections.md` containing my personal reflection on the drafted emails. My ranking is MGM Resorts first, Prologis second, and Arrow Security third. MGM's email had an appropriately corporate tone and effectively emphasized its worldwide locations. Prologis also has a large footprint across warehouses and other commercial settings, but its more nuanced needs call for greater personalization. Arrow Security ranks last because outreach concerning a potential partnership with another security company requires a more personalized approach due to the company's likely caution and additional partnership-development questions.

---

# Section 8: Human-Readable Dashboard

## Prompt 1

Create `dashboard.html` showing the company profile, target customers, contact information, and drafted emails in a format a person can easily review. Clearly show who the seller is, who the targets are, and that the emails are drafts that were not sent. Style the page similarly to the current ZeroEyes website, using the official logo and a compatible font and visual style where appropriate.

---

# Problem 9: Submission Package

## Prompt 1

Place all completed assignment files in a folder named `hw2` and create `hw2.zip` for submission. Do not include the `.env` file or any secrets.

---

## Section 3: Campus Customs Product Identification Agent

### Prompt 1

Create the Campus Customs agent as `prompts/prompt.md` (system prompt), `agent.py` (PydanticAI agent entry point), `tools.py` (agent tools and helper functions), and `models.py` (Pydantic/PydanticAI structured types). Implement the first ability: accept an image, decide whether a Campus Customs/Yale product appears, and identify the closest catalog product. Use the Assignment 3 data at `/Users/iin3rdyii/Desktop/DataHW3`, require confidence of at least 0.65, and send no more than 10 product reference images in a single inference batch. Wire the tool from `agent.py` and support `python agent.py --image "..."`.

### Prompt 2

Add to `output/harness.md` how product identification works, what makes it efficient, and which fields are in the identification model in `models.py` and why they were selected.

---

# Homework 4: React Shopping Site with a PydanticAI Agent

## Prompt 1

Start Homework 4 by creating and maintaining this `AI_prompts.md` file. All prompts, requirements, decisions, and assignment-related instructions shared during this conversation should be recorded here for grading.

## Prompt 2

Build a website or shopping site that includes an AI agent. Use React.js for the frontend and PydanticAI for the agent/backend. Begin the assignment with the same sections used previously, adding each new section and its prompts to this file as the work progresses.

---

# Homework 4: Section 2 — SQLite Product Data Harness

## Prompt 1

Create `output/harness.md` for the shopping-site project. Use the SQLite database at `/Users/iin3rdyii/Desktop/data/campus_customs.db` as the source of product data. The database contents will populate the website and provide the chatbot's product retrieval context.

The chatbot should search product type and product description, then return the matching product's price and other relevant fields. Treat this like a VLOOKUP-style operation: use the user's search criteria to find catalogue rows, then join each result to inventory by `product_id` so the response can include sizes and stock. Additional product data may be found in the Desktop `data` folder.

---

# Homework 4: Section 3 — Campus Customs Storefront Scaffold

## Prompt 1

Use the UX of https://yalebulldogblue.com/ as inspiration for the Campus Customs shopping site. Scaffold the frontend with React, Vite, and TypeScript. Add a top navigation bar linking to Home, Products, About Us, Login, and Create Account.

## Prompt 2

Use the product images and product data in the Desktop `data` folder and SQLite catalogue. Build an ecommerce-style catalog where each product card is clickable and opens a single-product view with the matching image, name, product type, description, price, and related information.

## Prompt 3

Add this About Us copy: “We are your number one solution for all Yale related merchandise, ran and operated by students; our focus is to provide apparael that shows the identity of our students and alumni. At Campus Customs we know that this isn't just an educational institution but an identity”.

## Prompt 4

Add a floating chat interface in the bottom-right corner. Create a fun, cute anime-inspired Handsome Dan mascot/avatar for the chat experience. Create a FastAPI application at `backend/admin.py` to support product retrieval and future chatbot integration.

---

# Homework 4: Section 4 — Secure Account Workflow

## Prompt 1

Build a normal create-account and login workflow using first name, last name, email, password, and confirm password. Enforce a strong password containing numbers, uppercase letters, lowercase letters, and special characters.

## Prompt 2

New accounts must be stored in the SQLite `users` table. Protect against SQL injection, XSF/XSS, and related input attacks. Hash passwords with SHA-256 using 120,000 iterations and a unique salt per password, using the same hash settings and salt handling during verification while ensuring password records do not match each other.

## Prompt 3

Encrypt sensitive personal account information as necessary. Update `output/harness.md` with the complete security design and safeguards.

---

# Homework 4: Section 5 — PydanticAI Shopping Chatbot

## Prompt 1

Build the shop chatbot with a PydanticAI agent behind FastAPI. Reuse the frontend chat widget and expose the API from `backend/main.py`, runnable from the `backend/` folder with `uvicorn main:app --reload --port 8000`. Keep the agent files next to it: `backend/prompts/prompt.md`, `backend/agent.py`, `backend/tools.py`, and `backend/models.py`.

## Prompt 2

Expose a chat route so a message from the website returns an agent reply using the configured AI API key and model. Put the Campus Customs voice and safety basics in `backend/prompts/prompt.md`. Define structured chat replies and product cards in `models.py`, and ground product answers in the SQLite catalogue tool.

---

# Homework 4: Section 6 — Grounded Price and Inventory Retrieval

## Prompt 1

Give the PydanticAI agent the ability to retrieve product descriptions, prices, and stock quantities from the Campus Customs SQLite database. The agent must use the database and must never invent prices or quantities. If an item or requested size is out of stock, say so clearly. Modify the SQL database only if needed.

## Prompt 2

Expand `backend/prompts/prompt.md` so price, description, and stock questions require database tools. Add or update return types in `backend/models.py`. In `output/harness.md`, list each database tool and explain which model fields are selected for lookup results and why.

---

# Homework 4: Section 7 — Dynamic Chat Product Cards

## Prompt 1

When a customer asks about an item type, such as “What hoodies do you have?”, the agent must search the catalogue and return structured matching products. The website must dynamically render those matches as product cards through the API contract.

## Prompt 2

Use the structured product matches efficiently and preserve the Section 3 single-item detail behavior. Every chat product card must open the same detail view when clicked. Update `backend/prompts/prompt.md` and `output/harness.md` to explain how search results reach the page.

---

# Homework 4: Section 8 — Chat Memory and Page Context

## Prompt 1

Save and reload chat history for logged-in shoppers using the database. Pass authenticated customer identity into agent dependencies or tools. Guests may chat but must not receive memory or inject persisted context.

## Prompt 2

Pass page context so the agent understands references to the current product, such as “Do you have this in pink?” Document storage, customer fields, guest behavior, and context propagation in `output/harness.md`.

---

# Homework 4: Section 9 — Ecommerce Usability

## Prompt 1

Fix the non-working Add to Cart button. Remove the tan palette and use a Yale aesthetic. Add subtle hover lift feedback for product cards. Make the cart section work so clicked products appear there with clear item information.

## Prompt 2

Replace the unclear heart icon with an understandable cart control. Before building, document each improvement and why it helps Campus Customs shoppers in `output/usability.md`. Explain that shoppers need to know what they are clicking and adding, and that hover feedback makes interactive products clearer and more inviting.

---

# Homework 4: Section 8 — Seasonal Yale Architectural Design

## Prompt 1

Create a living visual masterpiece by borrowing architectural design cues from Sterling Memorial Library and Yale campus buildings. Make the store feel like a real classical Yale shop with a fall seasonal layer, while preserving the Yale color palette.

## Prompt 2

Blend classical softness and Baroque painting qualities with playful 1990s magical-girl anime energy through typography, arches, stone geometry, sparkle details, and interactive product treatments. Make the page engaging for students, graduate students, and alumni. Document the design changes in `output/design.md`.

---

# Homework 4: Section 11 — Live Site QA

## Prompt 1

Create `output/app_check.html` as a live-site QA page with clear screenshots or visual panels and short captions for: chatbot inventory and honest pricing checks, dynamic category search result cards, and one usability feature. Include concise steps and pass conditions.

---

# Homework 4: Section 12 — Append-Only Audit and Safety

## Prompt 1

Maintain an append-only `output/audit_trail.json` of agent-loop activity, short result information, and stop reasons. Never wipe it. Keep the assistant constrained to the Campus Customs/Yale store.

## Prompt 2

The agent cannot inject or execute code, modify the database, change prices or inventory, access user information, expose secrets, browse the web, or accomplish unrelated tasks. Update `output/harness.md` with model fields and rationale, tools and abilities, safety rules, and system specifications. External web price comparisons are out of scope.
