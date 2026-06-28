import { NavLink } from "react-router-dom";

const links = [
  { to: "/bracket", label: "Bracket" },
  { to: "/fixtures", label: "Fixtures" },
  { to: "/teams", label: "Teams" },
  { to: "/model", label: "The model" }
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-line bg-pitch/85 backdrop-blur-xl">
      <nav className="mx-auto flex w-full max-w-[1240px] flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <NavLink
          to="/"
          className="flex items-baseline gap-2.5 font-display text-[21px] font-extrabold uppercase tracking-[0.04em] text-chalk"
        >
          MATCH<span className="text-gold">NIGHT</span>
        </NavLink>
        <div className="flex flex-wrap gap-1.5">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-sm border px-3.5 py-2 font-mono text-[11px] uppercase tracking-[0.1em] transition ${
                  isActive
                    ? "border-gold bg-gold font-bold text-pitch"
                    : "border-line text-chalk-dim hover:border-gold/40 hover:text-chalk"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  );
}
