import { FormEvent, useEffect, useState } from "react";
import {
  addAsset,
  Asset,
  createWatchlist,
  deleteWatchlist,
  listRecentAssets,
  listWatchlists,
  MarketsClientError,
  recordRecentAsset,
  removeAsset,
  renameWatchlist,
  reorderWatchlist,
  searchAssets,
  Watchlist
} from "./marketsApi";
import "./markets.css";

export function MarketsSurface({ profileRoot }: { profileRoot?: string }) {
  const [query, setQuery] = useState("");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [ambiguous, setAmbiguous] = useState(false);
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [newName, setNewName] = useState("");
  const [renameName, setRenameName] = useState("");
  const [recentAssets, setRecentAssets] = useState<Asset[]>([]);
  const [inspected, setInspected] = useState<Asset | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function reloadWatchlists() {
    if (!profileRoot) {
      setWatchlists([]);
      setSelected(null);
      return;
    }
    try {
      const rows = await listWatchlists(profileRoot);
      setWatchlists(rows);
      setSelected((value) => {
        if (value !== null && rows.some((row) => row.watchlist_id === value)) {
          return value;
        }
        return rows[0]?.watchlist_id ?? null;
      });
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function reloadRecentAssets() {
    if (!profileRoot) {
      setRecentAssets([]);
      return;
    }
    try {
      setRecentAssets(await listRecentAssets(profileRoot));
    } catch (error) {
      setNotice(message(error));
    }
  }

  useEffect(() => {
    void searchAssets("", profileRoot)
      .then((result) => setAssets(result.assets))
      .catch((error) => setNotice(message(error)));
  }, [profileRoot]);

  useEffect(() => {
    void reloadWatchlists();
    void reloadRecentAssets();
  }, [profileRoot]);

  useEffect(() => {
    const active = watchlists.find((row) => row.watchlist_id === selected);
    setRenameName(active?.name ?? "");
  }, [selected, watchlists]);

  async function submitSearch(event: FormEvent) {
    event.preventDefault();
    try {
      const result = await searchAssets(query, profileRoot);
      setAssets(result.assets);
      setAmbiguous(result.ambiguous);
      setNotice(
        result.ambiguous
          ? "Multiple canonical assets share that exact symbol. Choose by venue and name."
          : null
      );
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function inspect(asset: Asset) {
    setInspected(asset);
    if (!profileRoot) {
      return;
    }
    try {
      setRecentAssets(await recordRecentAsset(profileRoot, asset.asset_id));
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitWatchlist(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot) return;
    try {
      const row = await createWatchlist(profileRoot, newName);
      setNewName("");
      await reloadWatchlists();
      setSelected(row.watchlist_id);
      setNotice(null);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitRename(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || selected === null) return;
    try {
      await renameWatchlist(profileRoot, selected, renameName);
      await reloadWatchlists();
      setNotice("Watchlist renamed.");
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function add(assetId: string) {
    if (!profileRoot || selected === null) {
      setNotice("Create or select a watchlist first.");
      return;
    }
    try {
      await addAsset(profileRoot, selected, assetId);
      await reloadWatchlists();
      setNotice(null);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function remove(assetId: string) {
    if (!profileRoot || selected === null) return;
    try {
      await removeAsset(profileRoot, selected, assetId);
      await reloadWatchlists();
      setNotice(null);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function move(assetId: string, direction: -1 | 1) {
    if (!profileRoot || selected === null) return;
    const active = watchlists.find((row) => row.watchlist_id === selected);
    if (!active) return;
    const currentIndex = active.assets.findIndex((asset) => asset.asset_id === assetId);
    const targetIndex = currentIndex + direction;
    if (currentIndex < 0 || targetIndex < 0 || targetIndex >= active.assets.length) return;
    const reordered = active.assets.map((asset) => asset.asset_id);
    [reordered[currentIndex], reordered[targetIndex]] = [
      reordered[targetIndex],
      reordered[currentIndex]
    ];
    try {
      await reorderWatchlist(profileRoot, selected, reordered);
      await reloadWatchlists();
      setNotice(null);
    } catch (error) {
      setNotice(message(error));
    }
  }

  const active = watchlists.find((row) => row.watchlist_id === selected);

  return (
    <section className="markets" aria-labelledby="markets-heading">
      <header className="markets-hero">
        <div>
          <p className="eyebrow">D4 market browser</p>
          <h1 id="markets-heading">Markets</h1>
          <p>
            Search canonical assets, inspect local evidence availability, and organize
            profile-scoped watchlists. No streaming quotes or execution.
          </p>
        </div>
        <div className="markets-boundaries">
          <span>Offline-first</span>
          <span>Canonical IDs</span>
          <span>Research only</span>
        </div>
      </header>

      {notice ? (
        <div className="market-notice" role={ambiguous ? "status" : "alert"}>
          {notice}
        </div>
      ) : null}

      <div className="markets-layout">
        <section className="market-panel" aria-labelledby="browser-heading">
          <h2 id="browser-heading">Asset browser</h2>
          <form className="market-search" onSubmit={(event) => void submitSearch(event)}>
            <label htmlFor="market-query">Symbol, name, alias, or canonical ID</label>
            <div>
              <input
                id="market-query"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
              <button type="submit">Search</button>
            </div>
          </form>
          <ul className="asset-list">
            {assets.map((asset) => (
              <li key={asset.asset_id}>
                <div>
                  <strong>{asset.symbol}</strong>
                  <span>{asset.name}</span>
                  <small>{asset.asset_id}</small>
                  <small>
                    {asset.venue} · {asset.asset_class} · {asset.currency}
                  </small>
                  <small>Local data: {asset.availability.status}</small>
                </div>
                <div className="asset-actions">
                  <button type="button" onClick={() => void inspect(asset)}>
                    Inspect
                  </button>
                  <button
                    type="button"
                    disabled={!profileRoot}
                    onClick={() => void add(asset.asset_id)}
                  >
                    Add
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <aside className="market-panel watchlists" aria-labelledby="watchlists-heading">
          <h2 id="watchlists-heading">Watchlists</h2>
          {!profileRoot ? (
            <p>Open a profile to persist watchlists.</p>
          ) : (
            <>
              <form
                className="watchlist-create"
                onSubmit={(event) => void submitWatchlist(event)}
              >
                <label htmlFor="watchlist-name">New watchlist</label>
                <div>
                  <input
                    id="watchlist-name"
                    required
                    value={newName}
                    onChange={(event) => setNewName(event.target.value)}
                  />
                  <button type="submit">Create</button>
                </div>
              </form>

              <label htmlFor="watchlist-select">Active watchlist</label>
              <select
                id="watchlist-select"
                value={selected ?? ""}
                onChange={(event) => setSelected(Number(event.target.value))}
              >
                <option value="" disabled>
                  Select
                </option>
                {watchlists.map((row) => (
                  <option key={row.watchlist_id} value={row.watchlist_id}>
                    {row.name}
                  </option>
                ))}
              </select>

              {active ? (
                <>
                  <form className="watchlist-rename" onSubmit={(event) => void submitRename(event)}>
                    <label htmlFor="watchlist-rename">Rename active watchlist</label>
                    <div>
                      <input
                        id="watchlist-rename"
                        required
                        value={renameName}
                        onChange={(event) => setRenameName(event.target.value)}
                      />
                      <button type="submit">Rename</button>
                    </div>
                  </form>

                  <ul className="watchlist-assets">
                    {active.assets.map((asset, index) => (
                      <li key={asset.asset_id}>
                        <span>
                          <strong>{asset.symbol}</strong> {asset.venue}
                          <small>{asset.asset_id}</small>
                        </span>
                        <div className="watchlist-actions">
                          <button
                            type="button"
                            disabled={index === 0}
                            aria-label={`Move ${asset.symbol} up`}
                            onClick={() => void move(asset.asset_id, -1)}
                          >
                            Up
                          </button>
                          <button
                            type="button"
                            disabled={index === active.assets.length - 1}
                            aria-label={`Move ${asset.symbol} down`}
                            onClick={() => void move(asset.asset_id, 1)}
                          >
                            Down
                          </button>
                          <button type="button" onClick={() => void remove(asset.asset_id)}>
                            Remove
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                  <button
                    className="destructive"
                    type="button"
                    onClick={() =>
                      void deleteWatchlist(profileRoot, active.watchlist_id)
                        .then(() => reloadWatchlists())
                        .catch((error) => setNotice(message(error)))
                    }
                  >
                    Delete watchlist
                  </button>
                </>
              ) : (
                <p>No watchlist selected.</p>
              )}
            </>
          )}
        </aside>
      </div>

      <div className="markets-secondary-layout">
        <section className="market-panel" aria-labelledby="asset-details-heading">
          <h2 id="asset-details-heading">Asset details</h2>
          {inspected ? (
            <dl className="asset-details">
              <div>
                <dt>Canonical ID</dt>
                <dd>{inspected.asset_id}</dd>
              </div>
              <div>
                <dt>Name</dt>
                <dd>{inspected.name}</dd>
              </div>
              <div>
                <dt>Venue</dt>
                <dd>{inspected.venue}</dd>
              </div>
              <div>
                <dt>Aliases</dt>
                <dd>{inspected.aliases.length ? inspected.aliases.join(", ") : "None"}</dd>
              </div>
              <div>
                <dt>Local data</dt>
                <dd>{inspected.availability.status}</dd>
              </div>
              <div>
                <dt>Provenance</dt>
                <dd>{inspected.provenance}</dd>
              </div>
            </dl>
          ) : (
            <p>Inspect an asset to view canonical details.</p>
          )}
        </section>

        <section className="market-panel" aria-labelledby="recent-assets-heading">
          <h2 id="recent-assets-heading">Recent assets</h2>
          {!profileRoot ? (
            <p>Open a profile to retain recent assets.</p>
          ) : recentAssets.length ? (
            <ul className="recent-assets">
              {recentAssets.map((asset) => (
                <li key={asset.asset_id}>
                  <button type="button" onClick={() => void inspect(asset)}>
                    <strong>{asset.symbol}</strong>
                    <span>{asset.name}</span>
                    <small>{asset.asset_id}</small>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p>No recent assets yet. Inspect a search result to add it here.</p>
          )}
        </section>
      </div>
    </section>
  );
}

function message(error: unknown): string {
  return error instanceof MarketsClientError || error instanceof Error
    ? error.message
    : "Unexpected markets failure.";
}
