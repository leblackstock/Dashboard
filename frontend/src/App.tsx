import { DailyDashboard } from "./components/DailyDashboard";

export default function App() {
  return (
    <main className="dashboard-shell relative min-h-screen overflow-hidden px-4 py-6 text-ink sm:px-6 lg:px-8">
      <div className="dashboard-shell-glow pointer-events-none fixed inset-0 z-0" />
      <div className="relative z-10">
        <DailyDashboard />
      </div>
    </main>
  );
}
