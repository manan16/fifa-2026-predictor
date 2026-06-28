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
    <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/90 backdrop-blur-xl">
      <nav className="flex w-full flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between lg:px-10 2xl:px-16">
        <NavLink to="/" className="flex items-center gap-3 text-xl font-black tracking-normal text-white">
          <span className="grid h-9 w-9 place-items-center rounded-full border border-yellow-300/50 bg-emerald-900 text-yellow-300 shadow-gold">FC</span>
          FIFA 2026 Knockout Predictor
        </NavLink>
        <div className="flex flex-wrap gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `relative border-b-2 px-3 py-2 text-sm font-bold transition ${
                  isActive ? "border-yellow-300 text-yellow-300" : "border-transparent text-slate-300 hover:text-yellow-300"
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
