"""Optional plain SVG writer. The computational model never imports this module."""
from pathlib import Path
import html


def write_svg(data, destination):
    """Draw already prepared lists. No geometry checks or feasibility computation."""
    points = data["path_xy"] + data["samples_xy"]
    cx, cy = data["obstacle_center_xy"]
    radius = data["obstacle_radius_m"]
    xs = [point[0] for point in points] + [cx - radius, cx + radius]
    ys = [point[1] for point in points] + [cy - radius, cy + radius]
    low_x, low_y = min(xs), min(ys)
    width, height = max(max(xs) - low_x, 1.0), max(max(ys) - low_y, 1.0)
    scale = min(640.0 / width, 360.0 / height)
    def xy(point):
        return (60 + (point[0] - low_x) * scale, 440 - (point[1] - low_y) * scale)
    def coords(points):
        return " ".join(f"{x:.3f},{y:.3f}" for x, y in map(xy, points))
    x, y = xy([cx, cy])
    pieces = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="510" viewBox="0 0 760 510">',
              '<rect width="760" height="510" fill="white"/>',
              '<text x="30" y="30" font-family="Arial" font-size="18">Supplied path and sampled points (coordinates in metres)</text>',
              f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius * scale:.3f}" fill="#dddddd" stroke="black"/>',
              f'<polyline points="{coords(data["path_xy"])}" fill="none" stroke="black" stroke-width="2"/>']
    for point in data["samples_xy"]:
        x, y = xy(point)
        pieces.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3" fill="white" stroke="black"/>')
    for point, label in zip(data["path_xy"], data["labels"]):
        x, y = xy(point)
        text = html.escape(f"{label} {tuple(point)}")
        anchor = "end" if x > 380 else "start"
        pieces.append(f'<text x="{x:.3f}" y="{y - 10:.3f}" text-anchor="{anchor}" font-family="Arial" font-size="12">{text}</text>')
    pieces.append('<text x="30" y="495" font-family="Arial" font-size="13">This picture does not certify collision freedom or physical safety.</text></svg>')
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(pieces) + "\n", encoding="utf-8")
    return output
