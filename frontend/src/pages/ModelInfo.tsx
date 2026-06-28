import AnimatedPage from "../components/AnimatedPage";

export default function ModelInfo() {
  const sections = [
    {
      title: "Features",
      body: "The MVP combines Elo rating, FIFA ranking, neutral venue context, tournament stage, and a simple expected-goals transformation."
    },
    {
      title: "Generation",
      body: "Team strength is converted into projected goals. A compact Poisson score matrix turns those goal expectations into 90-minute win, draw, and loss probabilities."
    },
    {
      title: "Probabilities",
      body: "The output is probabilistic because football matches are noisy. A 58% favourite still loses often enough that uncertainty should remain visible."
    },
    {
      title: "Limitations",
      body: "Seeded data is illustrative. The current model does not yet include live squads, injuries, betting odds, xG history, rest days, travel, or tactical matchups."
    }
  ];

  return (
    <AnimatedPage className="space-y-6">
      <div>
        <p className="text-sm font-black uppercase text-gold">Prediction engine</p>
        <h1 className="mt-2 text-3xl font-black text-line">Model Info</h1>
        <p className="mt-2 max-w-3xl text-line/65">
          A deliberately simple baseline designed to be transparent, testable, and easy to replace with a trained model later.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {sections.map((section) => (
          <div key={section.title} className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
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
