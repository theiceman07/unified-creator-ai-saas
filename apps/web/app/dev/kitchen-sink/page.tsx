import { MonoLabel } from "@/components/ui/MonoLabel";
import { Hairline } from "@/components/ui/Hairline";
import { StatusDot } from "@/components/ui/StatusDot";
import { JudgeBadge } from "@/components/ui/JudgeBadge";
import { OriginChip } from "@/components/ui/OriginChip";
import { PaperSurface } from "@/components/ui/PaperSurface";
import { Button } from "@/components/ui/Button";

export default function KitchenSink() {
  return (
    <div className="p-8 max-w-4xl mx-auto space-y-12">
      <h1 className="text-h2 font-display">Design System Kitchen Sink</h1>
      
      <section className="space-y-4">
        <h2 className="text-h4">Colors & Themes</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="theme-dark p-6 rounded-md">
            <h3 className="text-text-lg mb-2">Dark Theme (Default Chrome)</h3>
            <p className="text-ink-400 text-sm">Text is paper-100, background is ink-900.</p>
          </div>
          <div className="theme-light p-6 rounded-md hairline">
            <h3 className="text-text-lg mb-2">Light Theme</h3>
            <p className="text-ink-600 text-sm">Text is ink-900, background is paper-300.</p>
          </div>
        </div>
      </section>
      
      <section className="space-y-4">
        <h2 className="text-h4">Typography</h2>
        <div className="space-y-2">
          <div className="text-display">Display</div>
          <div className="text-h1">Heading 1</div>
          <div className="text-h2">Heading 2</div>
          <div className="text-h3">Heading 3</div>
          <div className="text-h4">Heading 4</div>
          <div className="text-text-lg">Large Text Body</div>
          <div className="text-text">Regular Text Body</div>
          <div className="text-text-sm">Small Text</div>
        </div>
      </section>
      
      <section className="space-y-4">
        <h2 className="text-h4">Components</h2>
        <div className="flex flex-wrap gap-4 items-center">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="text">Text Link</Button>
          <MonoLabel>parenthetical label</MonoLabel>
          <StatusDot live={true} />
          <StatusDot />
          <JudgeBadge score={4.8} critique="Excellent" />
          <JudgeBadge score={3.2} critique="Needs work" />
          <JudgeBadge score={2.1} critique="Poor" />
          <OriginChip projectId="09" />
        </div>
        <div className="mt-4">
          <Hairline />
        </div>
      </section>
      
      <section className="space-y-4">
        <h2 className="text-h4">Paper Surface (Writing Area)</h2>
        <PaperSurface>
          <h3 className="text-text-lg mb-2">Generated Script</h3>
          <p className="text-text">
            This is what generated content looks like. It sits on a paper-200 surface with ink-900 text,
            resembling a real document against the dark chrome of the app.
          </p>
        </PaperSurface>
      </section>
    </div>
  );
}
