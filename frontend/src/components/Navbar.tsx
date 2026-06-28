import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/bracket", label: "Bracket" },
  { to: "/fixtures", label: "Knockout fixtures" },
  { to: "/teams", label: "Teams" },
  { to: "/model", label: "Model" }
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-line/10 bg-stadium/82 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
        <NavLink to="/" className="flex items-center gap-3 text-xl font-black tracking-normal text-line">
          <span className="grid h-9 w-9 place-items-center rounded-full border border-gold/40 bg-pitch shadow-gold">FC</span>
          FIFA 2026 Knockout Predictor
        </NavLink>
        <div className="flex flex-wrap gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `relative px-3 py-2 text-sm font-bold transition hover:text-gold ${
                  isActive ? "text-gold after:absolute after:inset-x-3 after:bottom-0 after:h-0.5 after:bg-gold" : "text-line/70"
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
