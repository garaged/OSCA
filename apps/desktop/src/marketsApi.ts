import { invoke } from "@tauri-apps/api/core";

export type Asset = {
  asset_id: string;
  asset_class: string;
  symbol: string;
  name: string;
  venue: string;
  currency: string;
  aliases: string[];
  provenance: string;
  availability: { status: string; timeframes: string[]; source: string | null };
};

export type Watchlist = {
  watchlist_id: number;
  name: string;
  created_at: string;
  updated_at: string;
  assets: Asset[];
};
export type AssetSearch = {
  query: string;
  total: number;
  ambiguous: boolean;
  exact_match_count: number;
  assets: Asset[];
  network_access_enabled: false;
};

export class MarketsClientError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly retryable = false
  ) {
    super(message);
    this.name = "MarketsClientError";
  }
}

export function searchAssets(
  query: string,
  profileRoot?: string
): Promise<AssetSearch> {
  return request(
    "asset.search",
    { query, ...(profileRoot ? { profile_root: profileRoot } : {}) },
    parseSearch
  );
}

export function getAsset(assetId: string, profileRoot?: string): Promise<Asset> {
  return request(
    "asset.get",
    { asset_id: assetId, ...(profileRoot ? { profile_root: profileRoot } : {}) },
    (row) => parseAsset(object(row.asset, "asset"))
  );
}

export function listRecentAssets(profileRoot: string): Promise<Asset[]> {
  return request(
    "asset.recent.list",
    { profile_root: profileRoot },
    (row) => array(row.assets, "assets").map((item) => parseAsset(object(item, "asset")))
  );
}

export function recordRecentAsset(profileRoot: string, assetId: string): Promise<Asset[]> {
  return request(
    "asset.recent.record",
    { profile_root: profileRoot, asset_id: assetId },
    (row) => array(row.assets, "assets").map((item) => parseAsset(object(item, "asset")))
  );
}

export function listWatchlists(profileRoot: string): Promise<Watchlist[]> {
  return request(
    "watchlist.list",
    { profile_root: profileRoot },
    (row) =>
      array(row.watchlists, "watchlists").map((item) =>
        parseWatchlist(object(item, "watchlist"))
      )
  );
}

export function createWatchlist(profileRoot: string, name: string): Promise<Watchlist> {
  return request(
    "watchlist.create",
    { profile_root: profileRoot, name },
    (row) => parseWatchlist(object(row.watchlist, "watchlist"))
  );
}

export function renameWatchlist(
  profileRoot: string,
  watchlistId: number,
  name: string
): Promise<Watchlist> {
  return request(
    "watchlist.rename",
    { profile_root: profileRoot, watchlist_id: watchlistId, name },
    (row) => parseWatchlist(object(row.watchlist, "watchlist"))
  );
}

export function deleteWatchlist(
  profileRoot: string,
  watchlistId: number
): Promise<void> {
  return request(
    "watchlist.delete",
    { profile_root: profileRoot, watchlist_id: watchlistId },
    () => undefined
  );
}

export function addAsset(
  profileRoot: string,
  watchlistId: number,
  assetId: string
): Promise<Watchlist> {
  return request(
    "watchlist.asset.add",
    { profile_root: profileRoot, watchlist_id: watchlistId, asset_id: assetId },
    (row) => parseWatchlist(object(row.watchlist, "watchlist"))
  );
}

export function removeAsset(
  profileRoot: string,
  watchlistId: number,
  assetId: string
): Promise<Watchlist> {
  return request(
    "watchlist.asset.remove",
    { profile_root: profileRoot, watchlist_id: watchlistId, asset_id: assetId },
    (row) => parseWatchlist(object(row.watchlist, "watchlist"))
  );
}

export function reorderWatchlist(
  profileRoot: string,
  watchlistId: number,
  assetIds: string[]
): Promise<Watchlist> {
  return request(
    "watchlist.reorder",
    { profile_root: profileRoot, watchlist_id: watchlistId, asset_ids: assetIds },
    (row) => parseWatchlist(object(row.watchlist, "watchlist"))
  );
}

async function request<T>(
  method: string,
  params: Record<string, unknown>,
  parse: (value: Record<string, unknown>) => T
): Promise<T> {
  const requestId = crypto.randomUUID();
  let raw: string;
  try {
    raw = await invoke<string>("desktop_request", {
      requestJson: JSON.stringify({
        protocol_version: "1.0",
        request_id: requestId,
        method,
        params
      })
    });
  } catch (error) {
    throw new MarketsClientError(
      "sidecar_unavailable",
      error instanceof Error ? error.message : "The OSCA sidecar is unavailable.",
      true
    );
  }
  const envelope = object(JSON.parse(raw) as unknown, "desktop response");
  if (text(envelope.request_id, "request_id") !== requestId) {
    throw new MarketsClientError(
      "invalid_response",
      "Desktop response identity did not match the request.",
      true
    );
  }
  if (text(envelope.status, "status") === "error") {
    const failure = object(envelope.error, "error");
    throw new MarketsClientError(
      text(failure.code, "error.code"),
      text(failure.message, "error.message"),
      Boolean(failure.retryable)
    );
  }
  return parse(object(envelope.result, "result"));
}

function parseSearch(row: Record<string, unknown>): AssetSearch {
  return {
    query: text(row.query, "query"),
    total: number(row.total, "total"),
    ambiguous: Boolean(row.ambiguous),
    exact_match_count: number(row.exact_match_count, "exact_match_count"),
    assets: array(row.assets, "assets").map((item) => parseAsset(object(item, "asset"))),
    network_access_enabled: false
  };
}

function parseAsset(row: Record<string, unknown>): Asset {
  const availability = object(row.availability, "availability");
  return {
    asset_id: text(row.asset_id, "asset_id"),
    asset_class: text(row.asset_class, "asset_class"),
    symbol: text(row.symbol, "symbol"),
    name: text(row.name, "name"),
    venue: text(row.venue, "venue"),
    currency: text(row.currency, "currency"),
    aliases: array(row.aliases, "aliases").map((item) => text(item, "alias")),
    provenance: text(row.provenance, "provenance"),
    availability: {
      status: text(availability.status, "availability.status"),
      timeframes: array(availability.timeframes, "timeframes").map((item) =>
        text(item, "timeframe")
      ),
      source:
        availability.source == null
          ? null
          : text(availability.source, "availability.source")
    }
  };
}

function parseWatchlist(row: Record<string, unknown>): Watchlist {
  return {
    watchlist_id: number(row.watchlist_id, "watchlist_id"),
    name: text(row.name, "name"),
    created_at: text(row.created_at, "created_at"),
    updated_at: text(row.updated_at, "updated_at"),
    assets: array(row.assets, "assets").map((item) => parseAsset(object(item, "asset")))
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new MarketsClientError("invalid_response", `${label} must be an object.`, true);
  }
  return value as Record<string, unknown>;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new MarketsClientError("invalid_response", `${label} must be an array.`, true);
  }
  return value;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string") {
    throw new MarketsClientError("invalid_response", `${label} must be a string.`, true);
  }
  return value;
}

function number(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new MarketsClientError("invalid_response", `${label} must be a number.`, true);
  }
  return value;
}
