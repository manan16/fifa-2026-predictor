import { CSSProperties } from "react";
import AnimatedPage from "../components/AnimatedPage";

export default function ModelInfo() {
  const sections = [
    {
      title: "Features",
      body: "Each team's strength blends its live Elo rating with a ranking-derived Elo, so FIFA ranking informs the baseline without simply double-counting a strong Elo or being capped at the top 100."
    },
    {
      title: "Scoreline",
      body: "A strength gap becomes an expected-goal supremacy, which is split around a stage-aware total-goals budget — later knockout rounds carry a smaller, tighter goal expectation than group games."
    },
    {
      title: "Probabilities",
      body: "Win, draw, and loss come from a Poisson score grid with a Dixon-Coles low-score correction, lifting realistic 0-0 and 1-1 outcomes that independent Poisson tends to understate."
    },
    {
      title: "Market & limits",
      body: "When betting consensus is available the model can blend toward it while keeping its own number visible. It still ignores live squads, injuries, rest, travel, and tactical matchups."
    }
  ];

  return (
    <AnimatedPage className="space-y-6">
      <div>
        <p className="text-sm font-black uppercase text-gold">Prediction engine</p>
        <h1 className="mt-2 text-3xl font-black text-line">Model Info</h1>
        <p className="mt-2 max-w-3xl text-line/65">
          A transparent supremacy-and-Poisson baseline with a Dixon-Coles draw correction — easy to reason about, and ready to be replaced by a trained model later.
        </p>
      </div>
      <div className="stagger-children grid gap-4 md:grid-cols-2">
        {sections.map((section, index) => (
          <div
            key={section.title}
            className="animate-card-in border border-line/10 bg-line/[0.06] p-5 shadow-broadcast"
            style={{ ["--i" as string]: index } as CSSProperties}
          >
            <h2 className="text-xl font-black text-gold">{section.title}</h2>
            <p className="mt-3 text-line/70">{section.body}</p>
          </div>
        ))}
      </div>
      <div className="border border-gold/25 bg-pitch p-5 text-line shadow-broadcast">
        <h2 className="text-xl font-black">Future improvements</h2>
        <p className="mt-3 text-line/75">
          Official fixture ingestion, historical international match pipelines, player availability, xG-based features, Brier score evaluation, and Monte Carlo bracket simulation.
        </p>
      </div>
    </AnimatedPage>
  );
}