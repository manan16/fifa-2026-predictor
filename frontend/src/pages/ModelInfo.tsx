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
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-black">Model Info</h1>
        <p className="mt-2 max-w-3xl text-ink/65">
          A deliberately simple baseline designed to be transparent, testable, and easy to replace with a trained model later.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {sections.map((section) => (
          <div key={section.title} className="bg-white p-5 shadow-sm">
            <h2 className="text-xl font-bold text-pitch">{section.title}</h2>
            <p className="mt-3 text-ink/70">{section.body}</p>
          </div>
        ))}
      </div>
      <div className="bg-ink p-5 text-white shadow-sm">
        <h2 className="text-xl font-bold">Future improvements</h2>
        <p className="mt-3 text-white/75">
          Official fixture ingestion, historical international match pipelines, player availability, xG-based features, Brier score evaluation, and Monte Carlo bracket simulation.
        </p>
      </div>
    </div>
  );
}

