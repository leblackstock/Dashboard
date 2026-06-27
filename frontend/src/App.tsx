import { DailyDashboard } from "./components/DailyDashboard";

export default function App() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#070a14] px-4 py-6 text-ink sm:px-6 lg:px-8">
      <div className="pointer-events-none fixed inset-0 z-0 bg-[linear-gradient(135deg,rgba(79,140,255,0.18)_0%,rgba(7,10,20,0)_28%),linear-gradient(180deg,#070a14_0%,#0b1020_58%,#0a0f1d_100%)]" />
      <div className="relative z-10">
        <DailyDashboard />
      </div>
    </main>
  );
}
