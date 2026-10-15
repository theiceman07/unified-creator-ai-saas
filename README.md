# CreatorOS

An AI creative operating system that takes a creator from idea → content → publishing → analytics → next idea in one workspace.

## Quickstart

1. Clone this repository
2. Ensure you have Node.js >= 18, `pnpm` >= 9, and `uv` installed.
3. Install dependencies:
   ```bash
   pnpm install
   cd apps/api && uv sync
   ```
4. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to add your LLM API keys
   ```
5. Start development servers:
   ```bash
   make dev
   ```
6. Run database migrations:
   ```bash
   make migrate
   ```
7. Seed the database with demo data:
   ```bash
   make seed
   ```
8. The web app is now running at `http://localhost:3000`
9. API is available at `http://localhost:8000`
