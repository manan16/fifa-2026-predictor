import { WatchLink } from "../types";

export default function WhereToWatchCard({ links }: { links: WatchLink[] }) {
  const link = links[0];
  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <h2 className="text-lg font-black text-white">Where to watch</h2>
      {link ? (
        <div className="mt-4">
          <p className="font-black text-white">{link.provider_name}</p>
          <p className="mt-1 text-sm text-slate-300">{link.region} · {link.provider_type.replace(/_/g, " ")}</p>
          {link.note && <p className="mt-3 text-sm text-slate-400">{link.note}</p>}
          <a href={link.url} target="_blank" rel="noreferrer" className="mt-4 inline-flex bg-yellow-400 px-4 py-2 text-sm font-black text-slate-950 transition hover:-translate-y-0.5">
            {link.provider_type === "official_match_centre" ? "Open match centre" : "Where to watch"}
          </a>
        </div>
      ) : (
        <p className="mt-4 text-sm font-bold text-slate-300">No official watch link is available yet.</p>
      )}
    </section>
  );
}
