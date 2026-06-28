import { Outlet } from "react-router-dom";
import FloodlightBg from "./FloodlightBg";
import Navbar from "./Navbar";

export default function Layout() {
  return (
    <div className="relative min-h-screen text-chalk">
      <FloodlightBg />
      <div className="relative z-10">
        <Navbar />
        <main className="mx-auto w-full max-w-[1240px] px-5 py-9">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
