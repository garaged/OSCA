import { FormEvent, useEffect, useState } from "react";
import { addAsset, Asset, createWatchlist, deleteWatchlist, listWatchlists, MarketsClientError, removeAsset, searchAssets, Watchlist } from "./marketsApi";
import "./markets.css";

export function MarketsSurface({ profileRoot }: { profileRoot?: string }) {
  const [query, setQuery] = useState("");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [ambiguous, setAmbiguous] = useState(false);
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [newName, setNewName] = useState("");
  const [notice, setNotice] = useState<string | null>(null);

  async function reloadWatchlists() {
    if (!profileRoot) { setWatchlists([]); return; }
    try { const rows = await listWatchlists(profileRoot); setWatchlists(rows); setSelected((value) => value ?? rows[0]?.watchlist_id ?? null); }
    catch (error) { setNotice(message(error)); }
  }
  useEffect(() => { void searchAssets("", profileRoot).then((result) => setAssets(result.assets)).catch((error) => setNotice(message(error))); }, [profileRoot]);
  useEffect(() => { void reloadWatchlists(); }, [profileRoot]);

  async function submitSearch(event: FormEvent) {
    event.preventDefault();
    try { const result = await searchAssets(query, profileRoot); setAssets(result.assets); setAmbiguous(result.ambiguous); setNotice(result.ambiguous ? "Multiple canonical assets share that exact symbol. Choose by venue and name." : null); }
    catch (error) { setNotice(message(error)); }
  }
  async function submitWatchlist(event: FormEvent) {
    event.preventDefault(); if (!profileRoot) return;
    try { const row = await createWatchlist(profileRoot, newName); setNewName(""); await reloadWatchlists(); setSelected(row.watchlist_id); }
    catch (error) { setNotice(message(error)); }
  }
  async function add(assetId: string) {
    if (!profileRoot || selected === null) { setNotice("Create or select a watchlist first."); return; }
    try { await addAsset(profileRoot, selected, assetId); await reloadWatchlists(); }
    catch (error) { setNotice(message(error)); }
  }
  async function remove(assetId: string) {
    if (!profileRoot || selected === null) return;
    try { await removeAsset(profileRoot, selected, assetId); await reloadWatchlists(); }
    catch (error) { setNotice(message(error)); }
  }

  const active = watchlists.find((row) => row.watchlist_id === selected);
  return <section className="markets" aria-labelledby="markets-heading">
    <header className="markets-hero"><div><p className="eyebrow">D4 market browser</p><h1 id="markets-heading">Markets</h1><p>Search canonical assets, inspect local evidence availability, and organize profile-scoped watchlists. No streaming quotes or execution.</p></div><div className="markets-boundaries"><span>Offline-first</span><span>Canonical IDs</span><span>Research only</span></div></header>
    {notice ? <div className="market-notice" role={ambiguous ? "status" : "alert"}>{notice}</div> : null}
    <div className="markets-layout">
      <section className="market-panel" aria-labelledby="browser-heading"><h2 id="browser-heading">Asset browser</h2><form className="market-search" onSubmit={(event) => void submitSearch(event)}><label htmlFor="market-query">Symbol, name, alias, or canonical ID</label><div><input id="market-query" value={query} onChange={(event) => setQuery(event.target.value)} /><button type="submit">Search</button></div></form><ul className="asset-list">{assets.map((asset) => <li key={asset.asset_id}><div><strong>{asset.symbol}</strong><span>{asset.name}</span><small>{asset.venue} · {asset.asset_class} · {asset.currency}</small><small>Local data: {asset.availability.status}</small></div><button type="button" disabled={!profileRoot} onClick={() => void add(asset.asset_id)}>Add</button></li>)}</ul></section>
      <aside className="market-panel watchlists" aria-labelledby="watchlists-heading"><h2 id="watchlists-heading">Watchlists</h2>{!profileRoot ? <p>Open a profile to persist watchlists.</p> : <><form className="watchlist-create" onSubmit={(event) => void submitWatchlist(event)}><label htmlFor="watchlist-name">New watchlist</label><div><input id="watchlist-name" required value={newName} onChange={(event) => setNewName(event.target.value)} /><button type="submit">Create</button></div></form><label htmlFor="watchlist-select">Active watchlist</label><select id="watchlist-select" value={selected ?? ""} onChange={(event) => setSelected(Number(event.target.value))}><option value="" disabled>Select</option>{watchlists.map((row) => <option key={row.watchlist_id} value={row.watchlist_id}>{row.name}</option>)}</select>{active ? <><ul className="watchlist-assets">{active.assets.map((asset) => <li key={asset.asset_id}><span><strong>{asset.symbol}</strong> {asset.venue}</span><button type="button" onClick={() => void remove(asset.asset_id)}>Remove</button></li>)}</ul><button className="destructive" type="button" onClick={() => void deleteWatchlist(profileRoot, active.watchlist_id).then(() => reloadWatchlists()).catch((error) => setNotice(message(error)))}>Delete watchlist</button></> : <p>No watchlist selected.</p>}</>}</aside>
    </div>
  </section>;
}

function message(error: unknown): string { return error instanceof MarketsClientError || error instanceof Error ? error.message : "Unexpected markets failure."; }
