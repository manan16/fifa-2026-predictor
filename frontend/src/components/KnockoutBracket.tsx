import { BracketFixture, BracketResponse } from "../types";
import BracketMatchCard from "./BracketMatchCard";
import BracketRound from "./BracketRound";
import ChampionCard from "./ChampionCard";

interface Props {
  bracket: BracketResponse;
}

const roundLabels = {
  round_of_32: "Round of 32",
  round_of_16: "Round of 16",
  quarter_finals: "Quarter-finals",
  semi_finals: "Semi-finals"
};

function bySide(fixtures: BracketFixture[], side: "Left bracket" | "Right bracket") {
  return fixtures.filter((fixture) => fixture.group_name === side);
}

export default function KnockoutBracket({ bracket }: Props) {
  const finalFixture = bracket.final[0];

  const leftRounds = [
    { title: roundLabels.round_of_32, fixtures: bySide(bracket.round_of_32, "Left bracket") },
    { title: roundLabels.round_of_16, fixtures: bySide(bracket.round_of_16, "Left bracket") },
    { title: roundLabels.quarter_finals, fixtures: bySide(bracket.quarter_finals, "Left bracket") },
    { title: roundLabels.semi_finals, fixtures: bySide(bracket.semi_finals, "Left bracket") }
  ];

  const rightRounds = [
    { title: roundLabels.semi_finals, fixtures: bySide(bracket.semi_finals, "Right bracket") },
    { title: roundLabels.quarter_finals, fixtures: bySide(bracket.quarter_finals, "Right bracket") },
    { title: roundLabels.round_of_16, fixtures: bySide(bracket.round_of_16, "Right bracket") },
    { title: roundLabels.round_of_32, fixtures: bySide(bracket.round_of_32, "Right bracket") }
  ];

  return (
    <div className="overflow-x-auto pb-4">
      <div className="flex min-w-[2360px] items-start justify-center gap-6">
        {leftRounds.map((round, index) => (
          <BracketRound key={`left-${round.title}`} title={round.title} fixtures={round.fixtures} direction="left" delay={index * 90} />
        ))}

        <section className="flex w-80 shrink-0 animate-card-in flex-col items-center gap-5 pt-20" style={{ animationDelay: "420ms" }}>
          <ChampionCard finalFixture={finalFixture} />
          <div>
            <h2 className="mb-4 text-center text-sm font-black uppercase text-white/65">Final</h2>
            {finalFixture ? (
              <BracketMatchCard fixture={finalFixture} />
            ) : (
              <div className="w-64 border border-dashed border-white/15 p-4 text-center text-sm text-white/45">TBD</div>
            )}
          </div>
        </section>

        {rightRounds.map((round, index) => (
          <BracketRound key={`right-${round.title}`} title={round.title} fixtures={round.fixtures} direction="right" delay={index * 90} />
        ))}
      </div>
    </div>
  );
}
