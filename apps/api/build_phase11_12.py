import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# --- Phase 11: End-to-End Seeds & Mock Types ---
write_file('app/demo/seed.py', """
import asyncio
import uuid
from app.db.session import SessionLocal
from app.db.models.models import Creator, VoiceProfile, Campaign

async def seed_db():
    async with SessionLocal() as session:
        # Create demo creator
        creator_id = uuid.uuid4()
        creator = Creator(
            id=creator_id,
            display_name="Demo Creator",
            is_demo=True,
            platforms=["youtube", "x"],
            goals=["audience_growth"]
        )
        session.add(creator)
        
        # Create voice profile
        voice = VoiceProfile(
            creator_id=creator_id,
            version=1,
            profile={"tone": "casual", "format": "hook_first"},
            is_active=True
        )
        session.add(voice)
        
        # Create test campaign
        campaign = Campaign(
            creator_id=creator_id,
            title="AI Agents for Beginners",
            topic="AI Agents",
            status="idea"
        )
        session.add(campaign)
        
        await session.commit()
        print("Database seeded with Demo Creator.")

if __name__ == "__main__":
    asyncio.run(seed_db())
""")

# --- Phase 12: Production Hardening (Error Boundaries & CI) ---
write_file('../web/app/global-error.tsx', """
'use client';
 
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="theme-dark min-h-screen flex flex-col items-center justify-center p-8">
        <h2 className="text-h2 font-display text-signal-fail mb-4">Something went critically wrong!</h2>
        <p className="text-ink-500 mb-8 font-mono">{error.message}</p>
        <button 
          onClick={() => reset()}
          className="px-6 py-3 bg-paper-100 text-ink-900 rounded-sm hover:bg-paper-200 transition-colors"
        >
          Try again
        </button>
      </body>
    </html>
  );
}
""")

write_file('../web/app/not-found.tsx', """
import Link from 'next/link';
import { MonoLabel } from '@/components/ui/MonoLabel';

export default function NotFound() {
  return (
    <div className="theme-dark min-h-screen flex flex-col items-center justify-center p-8">
      <h2 className="text-display font-display mb-4 opacity-50">404</h2>
      <p className="text-text-lg text-ink-500 mb-8">This module doesn't exist in the CreatorOS registry.</p>
      <Link href="/" className="px-6 py-3 bg-transparent text-paper-100 border hairline border-ink-700 hover:bg-ink-800 transition-colors">
        Return Home
      </Link>
    </div>
  );
}
""")

# Overwrite CI workflow to ensure it's hardened
write_file('../../.github/workflows/ci.yml', """
name: CreatorOS CI
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
    - name: Install Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        
    - name: Install pnpm
      run: npm install -g pnpm
        
    - name: Lint API
      run: |
        cd apps/api
        uv run ruff check .
        uv run mypy app
        
    - name: Test API
      run: |
        cd apps/api
        uv run pytest
        
    - name: Build Web
      run: |
        cd apps/web
        pnpm install
        pnpm build
""")

print("Phase 11 & 12 End-to-End & Hardening complete.")
