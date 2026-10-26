"""Small, child-friendly SVG showing repeated modular multiplication."""

from html import escape

import streamlit.components.v1 as components


def modular_cycle(N: int, a: int) -> list[int]:
    """Return 1, a mod N, ... through the first return to 1."""
    values = [1]
    while True:
        values.append((values[-1] * a) % N)
        if values[-1] == 1:
            return values


def render_cycle_visual(N: int, a: int, *, max_nodes: int = 9) -> int:
    """Render the multiplication trail and return its cycle length."""
    values = modular_cycle(N, a)
    period = len(values) - 1

    if len(values) <= max_nodes:
        visible = list(enumerate(values))
    else:
        head_size = max_nodes // 2
        tail_size = max_nodes - head_size - 1
        visible = list(enumerate(values[:head_size]))
        visible.append((None, None))
        visible.extend((i, values[i]) for i in range(len(values) - tail_size, len(values)))

    step = 92
    width = max(340, 46 + step * len(visible))
    centers = [58 + step * i for i in range(len(visible))]
    first_x, last_x = centers[0], centers[-1]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="205" viewBox="0 0 {width} 205" role="img" aria-label="Multiplying by {a} and taking remainders modulo {N} returns to 1 after {period} steps">',
        '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#718096"/></marker></defs>',
        '<rect width="100%" height="100%" rx="16" fill="#111827"/>',
        f'<path d="M {last_x} 82 C {last_x} 42, {first_x} 42, {first_x} 82" fill="none" stroke="#22d3ee" stroke-width="3" marker-end="url(#arrow)"/>',
        f'<text x="{(first_x + last_x) / 2}" y="17" text-anchor="middle" fill="#a5f3fc" font-family="sans-serif" font-size="14" font-weight="700">BACK TO 1 — the trail repeats!</text>',
    ]

    for visible_index, (power, remainder) in enumerate(visible):
        x = centers[visible_index]
        if visible_index < len(visible) - 1:
            next_x = centers[visible_index + 1]
            is_gap = visible[visible_index + 1][0] is None or power is None
            dash = ' stroke-dasharray="5 6"' if is_gap else ""
            svg.append(f'<path d="M {x + 31} 111 L {next_x - 34} 111" stroke="#718096" stroke-width="2"{dash} marker-end="url(#arrow)"/>')

        if power is None:
                skipped = len(values) - (max_nodes - 1)
            svg.extend([
                f'<circle cx="{x}" cy="111" r="27" fill="#374151" stroke="#9ca3af" stroke-dasharray="4 4"/>',
                f'<text x="{x}" y="117" text-anchor="middle" fill="#fff" font-family="sans-serif" font-size="18">…</text>',
                f'<text x="{x}" y="158" text-anchor="middle" fill="#cbd5e1" font-family="sans-serif" font-size="11">{skipped} turns</text>',
            ])
            continue

        is_repeat = power == period
        fill = "#16a34a" if power == 0 or is_repeat else f"hsl({(visible_index * 53 + 185) % 360}, 68%, 43%)"
        outline = "#facc15" if is_repeat else "#d1d5db"
        svg.append(f'<circle cx="{x}" cy="111" r="31" fill="{fill}" stroke="{outline}" stroke-width="{4 if is_repeat else 2}"/>')
        svg.append(f'<text x="{x}" y="117" text-anchor="middle" fill="#fff" font-family="sans-serif" font-size="18" font-weight="700">{remainder}</text>')
        caption = "START" if power == 0 else ("REPEATS" if is_repeat else f"step {power}")
        svg.append(f'<text x="{x}" y="160" text-anchor="middle" fill="#e5e7eb" font-family="sans-serif" font-size="12" font-weight="700">{escape(caption)}</text>')

    svg.append('</svg>')
    components.html(
        '<div style="overflow-x:auto; padding:4px 0">' + "".join(svg) + "</div>",
        height=220,
        scrolling=True,
    )
    return period
