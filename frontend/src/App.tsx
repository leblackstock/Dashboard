import { CodexUsageCard } from "./components/CodexUsageCard";

export default function App() {
  return (
    <main className="min-h-screen bg-[#0b1020] px-4 py-6 text-ink sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-5xl items-center">
        <CodexUsageCard />
      </div>
    </main>
  );
}
