import { MonoLabel } from '@/components/ui/MonoLabel';

export default function Home() {
  return (
    <div className="theme-dark min-h-screen p-8 max-w-5xl mx-auto flex flex-col gap-12">
      <div>
        <MonoLabel>thursday · 09:12</MonoLabel>
        <h1 className="text-display-sm font-display tracking-tight mt-4">Good morning, Creator.</h1>
      </div>
      
      <div className="bg-paper-200 text-ink-900 rounded-md p-6 text-xl">
        <input 
          type="text" 
          placeholder="What are you thinking about?_" 
          className="bg-transparent outline-none w-full placeholder-ink-500"
        />
      </div>
      
      <div>
        <MonoLabel>today's opportunities</MonoLabel>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
          <div className="border-l hairline border-ink-700 pl-4">
            <h3 className="text-h4">AI agents for beginners</h3>
            <p className="text-ink-500 text-sm mt-2">Trending topic (potential 82)</p>
            <button className="text-paper-100 hover:underline text-sm mt-4">Create campaign</button>
          </div>
          <div className="border-l hairline border-ink-700 pl-4">
            <h3 className="text-h4">"Agent vs chatbot?"</h3>
            <p className="text-ink-500 text-sm mt-2">From your audience (asked 14 times)</p>
            <button className="text-paper-100 hover:underline text-sm mt-4">Create campaign</button>
          </div>
        </div>
      </div>
    </div>
  );
}
