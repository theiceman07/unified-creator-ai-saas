import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

write_file('app/page.tsx', """
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { MonoLabel } from '@/components/ui/MonoLabel';

export default function LandingPage() {
  return (
    <main className="w-full">
      {/* SECTION 1: Light - Hero */}
      <section className="theme-light min-h-screen flex flex-col px-4 md:px-8">
        <nav className="flex justify-between items-center py-6">
          <div className="font-display font-bold text-h4">CreatorOS</div>
          <div className="hidden md:flex gap-6 items-center font-medium">
            <Link href="#product">Product</Link>
            <Link href="#how-it-works">How it works</Link>
            <Link href="#projects">Built from 27</Link>
            <Link href="#faq">FAQ</Link>
          </div>
          <Button variant="primary">Try the demo</Button>
        </nav>
        
        <div className="flex-1 flex flex-col justify-center items-start max-w-7xl mx-auto w-full relative z-10 pt-20 pb-32">
          <h1 className="text-display leading-[0.9] tracking-[-0.03em] font-display font-medium mb-8 uppercase">
            <div>One idea.</div>
            <div>Every platform.</div>
            <div>Your voice.</div>
          </h1>
          <p className="text-h4 max-w-3xl mb-12 text-ink-600">
            An AI creative operating system that turns one idea into a complete, on-voice content campaign — and learns from what performs.
          </p>
          <div className="flex items-center gap-6">
            <Button variant="primary" className="text-lg px-8 py-4 rounded-full">Start with a demo creator</Button>
            <MonoLabel>scroll to explore</MonoLabel>
          </div>
        </div>
      </section>

      {/* SECTION 2 & 3: Dark - Marquee & The Loop Scroll Story */}
      <section className="theme-dark py-section-lg px-4 md:px-8">
        <div className="overflow-hidden whitespace-nowrap mb-32 border-y hairline border-ink-700 py-4 opacity-50">
          <div className="animate-marquee inline-block font-display text-h3 tracking-widest uppercase space-x-12">
            <span>DISCOVER</span>
            <span>DECIDE</span>
            <span>CREATE</span>
            <span>PRODUCE</span>
            <span>REPURPOSE</span>
            <span>PUBLISH</span>
            <span>ANALYZE</span>
            <span>LEARN</span>
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto space-y-32">
          <h2 className="text-h2 max-w-4xl">
            Creators juggle 10 tools that forget who they are. CreatorOS unites them around a shared memory.
          </h2>
          
          <div className="space-y-32">
            {/* Stub for pinned scroll story */}
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(step => (
              <div key={step} className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center min-h-[50vh]">
                <div className="text-h1 font-display opacity-20">0{step}</div>
                <div className="bg-ink-800 aspect-video rounded-md hairline flex items-center justify-center">
                  <MonoLabel>looping screen capture {step}</MonoLabel>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 4: Light - Output Stories */}
      <section className="theme-light py-section-lg px-4 md:px-8">
        <div className="max-w-7xl mx-auto space-y-24">
          <MonoLabel>output stories</MonoLabel>
          
          <div className="grid grid-cols-1 gap-16">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div className="bg-paper-200 aspect-video rounded-md hairline flex justify-center items-center">
                <MonoLabel>demo capture</MonoLabel>
              </div>
              <div>
                <div className="text-display font-display font-medium tracking-tight mb-4">1 → 17</div>
                <h3 className="text-h3">1 podcast → 17 assets in 84 s</h3>
                <div className="mt-4"><MonoLabel>demo output</MonoLabel></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5: Dark - Built from 27 projects */}
      <section className="theme-dark py-section-lg px-4 md:px-8" id="projects">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-h2 mb-16">Built from 27 projects by 22 builders</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {Array.from({ length: 27 }).map((_, i) => (
              <div key={i} className="flex flex-col gap-2 p-6 rounded-sm border hairline border-ink-700 hover:bg-ink-800 transition-colors">
                <MonoLabel>#{String(i + 1).padStart(2, '0')}</MonoLabel>
                <div className="text-text-lg">Project Name Stub</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 6 & 7: Light - Memory & FAQ */}
      <section className="theme-light py-section-lg px-4 md:px-8" id="faq">
        <div className="max-w-7xl mx-auto space-y-32">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="p-8 border-x hairline border-paper-400">
              <h3 className="text-h4 mb-4">Voice Profile</h3>
              <p className="text-ink-600">Learns your tone, vocabulary, and patterns.</p>
            </div>
            <div className="p-8 border-r hairline border-paper-400">
              <h3 className="text-h4 mb-4">Content Library</h3>
              <p className="text-ink-600">Remembers everything you've ever said.</p>
            </div>
            <div className="p-8 border-r hairline border-paper-400">
              <h3 className="text-h4 mb-4">Insights</h3>
              <p className="text-ink-600">Tracks performance to feed the next idea.</p>
            </div>
          </div>
          
          <div className="max-w-3xl mx-auto space-y-8">
            <h2 className="text-h2 text-center mb-12">FAQ</h2>
            {/* Accordion stub */}
            <div className="border-b hairline border-paper-400 pb-4">
              <h3 className="text-h4">Does it post for me?</h3>
              <p className="text-ink-600 mt-2">No. CreatorOS proposes; you decide. We never auto-publish without approval.</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 8: Dark - Closing CTA & Footer */}
      <section className="theme-dark py-section-lg px-4 md:px-8 flex flex-col items-center justify-center min-h-[80vh] text-center">
        <h2 className="text-display font-display leading-[0.9] tracking-tight uppercase mb-12">
          <div>Turn one idea</div>
          <div>into a week</div>
          <div>of content</div>
        </h2>
        <Button variant="primary" className="text-lg px-8 py-4 rounded-full mb-32">Start with a demo creator</Button>
        
        <footer className="w-full max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center text-ink-500 text-sm border-t hairline border-ink-700 pt-8 mt-auto">
          <div>© {new Date().getFullYear()} CreatorOS</div>
          <div className="flex gap-4">
            <Link href="#" className="hover:text-paper-100">Ask Claude about us</Link>
            <Link href="#" className="hover:text-paper-100">Ask ChatGPT about us</Link>
          </div>
          <div>Live Timezone Stub</div>
        </footer>
      </section>
    </main>
  );
}
""")

print("Phase 5 marketing landing page generated.")
