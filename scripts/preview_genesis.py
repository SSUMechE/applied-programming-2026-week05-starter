"""Provided optional display of the student's model. No physics or safety test.

Run from this repository after the core TODOs, in the existing CUDA environment.
Only the two supplied cases are accepted. Numerical evaluation happens before
graphics imports and is never replaced by a reference answer.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
import hashlib
import html
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback
import uuid


PROFILES = {
    "low": {"width": 640, "height": 480, "fps": 10, "frames": 40},
    "standard": {"width": 960, "height": 720, "fps": 15, "frames": 60},
}
RENDER_TIMEOUT_SECONDS = 240
ROOT = Path(__file__).resolve().parents[1]
DISCLAIMER = (
    "Prescribed geometric replay, not a physical simulation or safety certificate. "
    "The cube marks a point. Its size and the disk height are display-only."
)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def output_directory(args):
    limit = repr(args.max_length).removesuffix(".0").replace(".", "p").replace("-", "m")
    return ROOT / "artifacts" / "genesis" / f"{args.case}_{args.method}_L{limit}_{args.profile}"


def write_page(destination, data, status, prefix=""):
    """The latest page always identifies this run, including a failed new run."""
    result = html.escape(json.dumps(data["evaluation"], indent=2, allow_nan=False))
    title = html.escape(f"{data['case']} / {data['settings']['method']} / {data['profile']}")
    message = html.escape(status["message"])
    video = (f'<video controls loop playsinline preload="metadata" src="{prefix}preview.mp4"></video>'
             if status["status"] == "complete" else "<p>No completed movie for this run.</p>")
    destination.write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Week 5 optional Genesis view</title>
<style>body{{max-width:960px;margin:24px auto;padding:0 18px;font:18px/1.5 sans-serif;color:#111;background:white}}
video{{width:100%;max-width:960px;border:1px solid black}}pre{{white-space:pre-wrap;border:1px solid black;padding:14px}}
code{{overflow-wrap:anywhere}}</style>
<h1>Week 5: same path, selected checks</h1><h2>{title}</h2>
<p>{message}</p>{video}
<p>Black dots are checked samples. The orange cube moves along the supplied path.
It is not another checked sample. All x/y coordinates are in metres.</p>
<p>{html.escape(DISCLAIMER)}</p>
<h2>Actual model return</h2><pre>{result}</pre>
<p>This is the saved return from your <code>evaluate()</code>, not a reference solution.
The picture uses your <code>to_plot_data()</code>. A displayed True applies only to the selected checks.</p>
<p><a href="{prefix}result.json">Saved numerical result and display data</a> |
<a href="{prefix}render.json">Rendering status</a></p>
<p>Nothing here is submitted. If graphics fail, return to the Week 5 environment
and continue with numerical tests or <code>python scripts/render_preview.py</code>.</p>
<p>Run: <code>{html.escape(data['run_id'])}</code></p></html>''', encoding="utf-8")


def prepare_result(args, run_id):
    # Import this repository's installed package, not a supplied reference copy.
    import ap_week05
    from ap_week05 import ParametricPlanningProblem, PlanningSettings, supplied_case
    from ap_week05.domain import Path as ModelPath

    package_file = Path(ap_week05.__file__).resolve()
    if package_file.parent != (ROOT / "src" / "ap_week05").resolve():
        raise RuntimeError("ap_week05 is not imported from this repository. Follow the optional local-package command.")
    inputs = supplied_case()
    if args.case == "direct":
        inputs["path"] = ModelPath((inputs["start"], inputs["goal"]))
    settings = PlanningSettings(max_length_m=args.max_length, method=args.method)
    problem = ParametricPlanningProblem(**inputs, settings=settings)
    evaluation = asdict(problem.evaluate())
    data = {
        "schema": "week05-optional-genesis-v1", "run_id": run_id,
        "case": args.case, "profile": args.profile, "settings": asdict(settings),
        "evaluation": evaluation,
        "bounds": {"lower": list(problem.bounds.lower.values), "upper": list(problem.bounds.upper.values)},
        "provenance": {"package_file": str(package_file), "evaluation": "student problem.evaluate()",
                       "display": "student problem.to_plot_data()",
                       "model_sha256": hashlib.sha256((package_file.parent / "model.py").read_bytes()).hexdigest(),
                       "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "note": DISCLAIMER,
    }
    return problem, data


def write_model_failure(destination, run_id, message):
    """Invalidate a previous success without inventing a result or deleting history."""
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Week 5 model evaluation stopped</title>
<style>body{{max-width:800px;margin:24px auto;padding:0 18px;font:18px/1.5 sans-serif;color:black;background:white}}</style>
<h1>Model evaluation stopped</h1><h2>No new numerical result or movie</h2>
<p>{html.escape(message)}</p>
<p>Complete the core model and its required checks first. No reference answer was substituted.</p>
<p>Previous run folders are preserved, but this attempt did not produce a successful preview.</p>
<p>Latest attempt: <code>{html.escape(run_id)}</code></p></html>''', encoding="utf-8")


def validate_display(data):
    """Bound display work only. Do not calculate or repair an evaluation verdict."""
    plot = data["plot_data"]
    for key, minimum, maximum in (("path_xy", 2, 32), ("samples_xy", 1, 64)):
        points = plot[key]
        if not isinstance(points, list) or not minimum <= len(points) <= maximum:
            raise ValueError(f"{key} exceeds the bounded optional display size")
        for point in points:
            if (not isinstance(point, list) or len(point) != 2
                    or any(type(v) not in (int, float) or not math.isfinite(v) for v in point)
                    or not (-1 <= point[0] <= 5 and -1 <= point[1] <= 3)):
                raise ValueError(f"{key} contains a point outside the supplied display scene")
    centre = plot["obstacle_center_xy"]
    radius = plot["obstacle_radius_m"]
    if centre != [2.0, 0.0] or type(radius) not in (int, float) or radius != 0.5:
        raise ValueError("The optional viewer accepts only the supplied disk")
    return plot


def render_movie(run_dir, data):
    """CUDA kinematic state + OpenGL Rasterizer. No contact solver or dynamics."""
    started = time.perf_counter()
    plot = validate_display(data)
    import importlib.metadata
    import numpy as np
    import torch
    import genesis as gs
    import imageio_ffmpeg
    from PIL import Image, ImageDraw, ImageFont

    if not torch.cuda.is_available() or torch.version.cuda is None:
        raise RuntimeError("CUDA is unavailable. Complete the separate CUDA checks first.")
    torch.cuda.reset_peak_memory_stats()
    profile = PROFILES[data["profile"]]
    width, height, fps = profile["width"], profile["height"], profile["fps"]
    gs.init(backend=gs.cuda, precision="32", logging_level="warning", performance_mode=False)
    if gs.backend != gs.cuda or gs.device.type != "cuda":
        raise RuntimeError("Genesis did not initialize on CUDA")
    encoder = None
    encoder_log = None
    snapshots = []

    def memory(label):
        torch.cuda.synchronize()
        free, total = torch.cuda.mem_get_info()
        snapshots.append({"phase": label, "device_free_mib": free / 2**20,
                          "device_total_mib": total / 2**20,
                          "torch_allocated_mib": torch.cuda.memory_allocated() / 2**20,
                          "torch_reserved_mib": torch.cuda.memory_reserved() / 2**20})

    try:
        memory("after_init")
        scene = gs.Scene(
            show_viewer=False, renderer=gs.renderers.Rasterizer(),
            sim_options=gs.options.SimOptions(dt=1 / fps, gravity=(0, 0, 0)),
            vis_options=gs.options.VisOptions(
                shadow=False, plane_reflection=False, background_color=(1, 1, 1),
                ambient_light=(0.65, 0.65, 0.65),
                lights=[dict(type="directional", dir=(-1, -1, -2), color=(1, 1, 1), intensity=2.0)]),
        )
        kin = gs.materials.Kinematic()

        def add(morph, color):
            return scene.add_entity(morph, material=kin, surface=gs.surfaces.Default(color=color))

        add(gs.morphs.Box(pos=(2, 1, -0.025), size=(6, 4, 0.05), collision=False), (0.94, 0.94, 0.94))
        add(gs.morphs.Cylinder(pos=(2, 0, 0.012), radius=0.5, height=0.024, collision=False), (0.64, 0.64, 0.64))
        route = np.asarray(plot["path_xy"], dtype=float)
        lengths = np.linalg.norm(np.diff(route, axis=0), axis=1)
        if not np.isfinite(lengths).all() or (lengths <= 0).any():
            raise ValueError("The supplied display route needs nonzero finite segments")
        for left, right, length in zip(route[:-1], route[1:], lengths):
            midpoint = (left + right) / 2
            angle = math.degrees(math.atan2(right[1] - left[1], right[0] - left[0]))
            add(gs.morphs.Box(pos=(*midpoint, 0.037), size=(float(length), 0.025, 0.016),
                              euler=(0, 0, angle), collision=False), (0.18, 0.30, 0.48))
        for point in plot["samples_xy"]:
            add(gs.morphs.Sphere(pos=(*point, 0.075), radius=0.050, collision=False), (0.03, 0.03, 0.03))
        marker = add(gs.morphs.Box(pos=(*route[0], 0.17), size=(0.16, 0.16, 0.16), collision=False),
                     (1.0, 0.48, 0.05))
        camera = scene.add_camera(res=(width, height), pos=(2, -4.2, 6.5), lookat=(2, 1, 0), fov=43, GUI=False)
        scene.build()
        if marker.get_pos().device.type != "cuda":
            raise RuntimeError("The display state is not on CUDA")
        memory("after_build")
        build_seconds = time.perf_counter() - started
        font = ImageFont.load_default(size=18 if width == 640 else 26)
        small = ImageFont.load_default(size=15 if width == 640 else 22)
        encoder_log = (run_dir / "encoding.log").open("wb")
        encoder = subprocess.Popen(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
             "-s", f"{width}x{height}", "-pix_fmt", "rgb24", "-r", str(fps), "-i", "-", "-an",
             "-vcodec", "libx264", "-crf", "24", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
             "-threads", "1", "-movflags", "+faststart", str(run_dir / "preview.mp4")],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=encoder_log,
        )
        cumulative = np.r_[0.0, np.cumsum(lengths)]
        result = data["evaluation"]
        timeline = []
        for frame in range(profile["frames"]):
            # Replay speed is a display choice. It is independent of checked samples.
            fraction = min(1.0, max(0.0, (frame / profile["frames"] - 0.1) / 0.8))
            distance = fraction * cumulative[-1]
            segment = min(int(np.searchsorted(cumulative[1:], distance, side="right")), len(lengths) - 1)
            alpha = (distance - cumulative[segment]) / lengths[segment]
            point = route[segment] + alpha * (route[segment + 1] - route[segment])
            marker.set_pos((*point, 0.17), relative=False)
            scene.visualizer.update()
            rgb = camera.render(rgb=True)[0]
            picture = Image.fromarray(rgb)
            if frame in (0, profile["frames"] // 2 - 1, profile["frames"] // 2, profile["frames"] - 1):
                picture.save(run_dir / f"raw_frame_{frame:03d}.png")
            draw = ImageDraw.Draw(picture)
            scale = width / 640
            draw.rectangle((0, 0, width - 1, round(70 * scale)), fill="white", outline="black")
            draw.text((12, 8), f"{data['case']} / {data['settings']['method']}   sampled feasible: {result['feasible']}",
                      fill="black", font=font)
            draw.text((12, round(37 * scale)),
                      f"samples: {result['sample_count']}   clearance margin: {result['clearance_margin_m']:.3g} m   length margin: {result['length_margin_m']:.3g} m",
                      fill="black", font=small)
            footer = height - round(70 * scale)
            draw.rectangle((0, footer, width - 1, height - 1), fill="white", outline="black")
            draw.text((12, footer + 7), "Black dots: checked samples. Orange cube: moving point marker.", fill="black", font=small)
            draw.text((12, footer + round(31 * scale)), "Metres. Display-only replay. No robot radius or safety certificate.", fill="black", font=small)
            encoder.stdin.write(np.ascontiguousarray(picture, dtype=np.uint8).tobytes())
            if frame in (0, profile["frames"] // 2 - 1, profile["frames"] // 2, profile["frames"] - 1):
                picture.save(run_dir / f"frame_{frame:03d}.png")
            timeline.append({"frame": frame, "marker_xy": point.tolist()})
        encoder.stdin.close()
        if encoder.wait(timeout=30):
            raise RuntimeError("Video encoding failed. See encoding.log.")
        memory("after_frames")
        report = {
            "status": "complete", "message": "Optional movie completed. Read the actual model result below.",
            "backend": "cuda", "renderer": "Rasterizer (OpenGL)", "device": str(gs.device),
            "gpu": torch.cuda.get_device_name(), "torch": torch.__version__, "torch_cuda": torch.version.cuda,
            "genesis": importlib.metadata.version("genesis-world"), "profile": profile,
            "frames": len(timeline), "duration_seconds": len(timeline) / fps,
            "build_and_import_seconds": build_seconds, "wall_seconds": time.perf_counter() - started,
            "torch_peak_allocated_mib": torch.cuda.max_memory_allocated() / 2**20,
            "torch_peak_reserved_mib": torch.cuda.max_memory_reserved() / 2**20,
            "memory_snapshots": snapshots,
            "memory_note": "Torch allocator excludes Genesis/OpenGL allocations. Device free/total includes other processes. These are snapshots, not whole-process peak VRAM.",
            "note": DISCLAIMER,
        }
        write_json(run_dir / "timeline.json", timeline)
        write_json(run_dir / "render.json", report)
    finally:
        if encoder is not None and encoder.poll() is None:
            if encoder.stdin and not encoder.stdin.closed:
                encoder.stdin.close()
            try:
                encoder.wait(timeout=10)
            except subprocess.TimeoutExpired:
                encoder.kill()
                encoder.wait()
        if encoder_log is not None:
            encoder_log.close()
        gs.destroy()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("direct", "detour"), default="detour")
    parser.add_argument("--method", choices=("waypoints", "interpolated"), default="interpolated")
    parser.add_argument("--max-length", type=float, default=9.0)
    parser.add_argument("--profile", choices=tuple(PROFILES), default="low")
    parser.add_argument("--_render-run", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not math.isfinite(args.max_length) or not 0 < args.max_length <= 20:
        parser.error("--max-length must be finite and in (0, 20]")
    destination = output_directory(args)
    if args._render_run is not None:
        if not re.fullmatch(r"\d{8}_\d{6}_\d{6}_[0-9a-f]{8}", args._render_run):
            parser.error("invalid internal run identifier")
        run_dir = destination / "runs" / args._render_run
        try:
            data = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
            render_movie(run_dir, data)
        except Exception as error:
            traceback.print_exc()
            write_json(run_dir / "render.json", {"status": "failed", "message": f"{type(error).__name__}: {error}"})
            return 3
        return 0

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "_" + uuid.uuid4().hex[:8]
    try:
        problem, data = prepare_result(args, run_id)
        # Check serializability before creating an artifact. Never allow JSON NaN.
        json.dumps(data, allow_nan=False)
    except NotImplementedError as error:
        message = f"Core model is unfinished ({error}). Complete TODOs 1-3 and required tests first. No reference answer was substituted."
        write_model_failure(destination, run_id, message)
        print(message, file=sys.stderr)
        return 2
    except Exception as error:
        message = f"Model evaluation stopped: {type(error).__name__}: {error}"
        write_model_failure(destination, run_id, message)
        print(message, file=sys.stderr)
        print("Use the Week 5 numerical checks first. No movie was attempted.", file=sys.stderr)
        return 2
    run_dir = destination / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    write_json(run_dir / "result.json", data)
    print("Actual model result:", json.dumps(data["evaluation"], allow_nan=False), flush=True)
    status = {"status": "pending", "message": "Numerical result saved. Optional graphics are not yet complete."}
    write_json(run_dir / "render.json", status)
    prefix = f"runs/{run_id}/"
    write_page(run_dir / "index.html", data, status)
    write_page(destination / "index.html", data, status, prefix)
    try:
        data["plot_data"] = problem.to_plot_data()
        # Serialize in memory first so a bad display return cannot truncate saved numbers.
        encoded = json.dumps(data, indent=2, allow_nan=False)
        (run_dir / "result.json").write_text(encoded + "\n", encoding="utf-8")
        validate_display(data)
        command = [sys.executable, str(Path(__file__).resolve()), "--case", args.case, "--method", args.method,
                   "--max-length", repr(args.max_length), "--profile", args.profile, "--_render-run", run_id]
        with (run_dir / "render.log").open("w", encoding="utf-8") as log:
            completed = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                       timeout=RENDER_TIMEOUT_SECONDS, check=False)
        status = json.loads((run_dir / "render.json").read_text(encoding="utf-8"))
        if completed.returncode or status["status"] != "complete" or not (run_dir / "preview.mp4").is_file():
            raise RuntimeError(status.get("message", "Graphics did not complete") if status["status"] != "pending"
                               else f"Graphics process exited {completed.returncode}. See render.log.")
    except Exception as error:
        status = {"status": "failed", "message": f"Optional rendering unavailable: {type(error).__name__}: {error}"}
        write_json(run_dir / "render.json", status)
        print(status["message"], file=sys.stderr)
        print("Numerical result is preserved. Continue with core tests or the SVG preview. Nothing extra is submitted.", file=sys.stderr)
    write_page(run_dir / "index.html", data, status)
    write_page(destination / "index.html", data, status, prefix)
    print("Open", (destination / "index.html").relative_to(ROOT).as_posix(), flush=True)
    print("Saved numbers:", (run_dir / "result.json").relative_to(ROOT).as_posix(), flush=True)
    return 0 if status["status"] == "complete" else 3


if __name__ == "__main__":
    raise SystemExit(main())
