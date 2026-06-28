import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/fixtures", label: "Knockout fixtures" },
  { to: "/teams", label: "Teams" },
  { to: "/model", label: "Model" }
];

export default function Navbar() {
  return (
    <header className="border-b border-ink/10 bg-white">
      <nav className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
        <NavLink to="/" className="text-xl font-bold tracking-normal text-pitch">
          FIFA 2026 Knockout Predictor
        </NavLink>
        <div className="flex flex-wrap gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `px-3 py-2 text-sm font-semibold ${
                  isActive ? "bg-pitch text-white" : "bg-sand text-ink hover:bg-gold/30"
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
