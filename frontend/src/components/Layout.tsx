import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
  return (
    <div className="min-h-screen bg-stadium">
      <Navbar />
      <main className="w-full px-4 py-8 text-line sm:px-6 lg:px-10 2xl:px-16">
        <Outlet />
      </main>
    </div>
  );
}
