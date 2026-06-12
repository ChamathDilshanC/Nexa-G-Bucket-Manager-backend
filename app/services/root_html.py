"""HTML landing page renderer for the API root endpoint.

Author: Chamath Dilshan
"""

import html

from app.schemas.info import ApiLink, RootResponse


def _link(url: str, label: str) -> str:
    """Render an external link that opens in a new browser tab."""
    safe_url = html.escape(url, quote=True)
    safe_label = html.escape(label)
    return (
        f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_label}</a>'
    )


def _render_link_row(link: ApiLink) -> str:
    """Render a single API endpoint row."""
    auth_badge = (
        '<span class="badge auth">Auth</span>' if link.auth_required else '<span class="badge">Public</span>'
    )
    return f"""
    <tr>
      <td><span class="method">{html.escape(link.method)}</span></td>
      <td>{html.escape(link.name)}</td>
      <td>{_link(link.url, link.path)}</td>
      <td>{auth_badge}</td>
      <td>{html.escape(link.description)}</td>
    </tr>
    """


def build_root_html(payload: RootResponse) -> str:
    """Build a browser-friendly HTML landing page with clickable endpoint links."""
    docs_rows = "".join(
        f"<li>{_link(getattr(payload.docs, key).url, getattr(payload.docs, key).name)}</li>"
        for key in ("swagger", "redoc", "openapi")
    )
    endpoint_rows = "".join(_render_link_row(link) for link in payload.links)
    connectivity = payload.connectivity
    settings = payload.settings

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(payload.name)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #0f172a;
      --card: #111827;
      --text: #e5e7eb;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --border: #1f2937;
      --ok: #22c55e;
      --warn: #f59e0b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
      color: var(--text);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 48px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    h1 {{ font-size: 2rem; }}
    h2 {{ font-size: 1.1rem; color: var(--accent); }}
    p {{ color: var(--muted); }}
    .grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      margin: 24px 0;
    }}
    .card {{
      background: rgba(17, 24, 39, 0.9);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
    }}
    .status {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(34, 197, 94, 0.15);
      color: var(--ok);
      font-size: 0.85rem;
      font-weight: 600;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
    a:hover {{ text-decoration: underline; }}
    ul {{ margin: 0; padding-left: 18px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 0.95rem;
    }}
    th, td {{
      border-bottom: 1px solid var(--border);
      padding: 12px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    .method {{
      display: inline-block;
      min-width: 52px;
      font-weight: 700;
      color: #fbbf24;
      font-family: Consolas, monospace;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(148, 163, 184, 0.15);
      color: var(--muted);
      font-size: 0.75rem;
    }}
    .badge.auth {{
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
    }}
    .meta {{ margin-top: 8px; font-size: 0.9rem; color: var(--muted); }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>{html.escape(payload.name)}</h1>
    <p>{html.escape(payload.description)}</p>
    <div class="meta">
      Version {html.escape(payload.version)} · Environment {html.escape(payload.environment)}
      · <span class="status">{html.escape(payload.status)}</span>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Connectivity</h2>
        <p>Overall: <strong>{html.escape(connectivity.overall_status)}</strong></p>
        <p>Supabase: {"connected" if connectivity.supabase_connected else "disconnected"}</p>
        <p>Storage: {"connected" if connectivity.storage_connected else "disconnected"}</p>
        <p>Default bucket: {html.escape(connectivity.default_bucket or "not set")}</p>
        <p>Total buckets: {connectivity.total_buckets}</p>
      </div>
      <div class="card">
        <h2>Documentation</h2>
        <ul>{docs_rows}</ul>
        <p class="meta">Full status: {_link(payload.detailed_status_url, "/info")}</p>
      </div>
      <div class="card">
        <h2>Settings</h2>
        <p>Upload limit: {settings.max_upload_size_mb} MB</p>
        <p>Signed URL expiry: {settings.signed_url_expiry_seconds}s</p>
        <p>MIME types: {html.escape(", ".join(settings.allowed_mime_types))}</p>
      </div>
    </div>

    <div class="card">
      <h2>API Endpoints</h2>
      <p>Click a path to open the endpoint in a new tab.</p>
      <table>
        <thead>
          <tr>
            <th>Method</th>
            <th>Name</th>
            <th>Path</th>
            <th>Access</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {endpoint_rows}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>"""
