import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
  return (
    <div className="min-h-screen bg-stadium">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8 text-line">
        <Outlet />
      </main>
    </div>
  );
}
