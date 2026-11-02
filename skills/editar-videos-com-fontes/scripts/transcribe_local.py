#!/usr/bin/env python3
"""Local ASR via faster-whisper → Whisper-style word JSON for import_words.py.

Usage:
  python3 transcribe_local.py INPUT.mp4 -o whisper.json
  python3 transcribe_local.py INPUT.mp4 -o whisper.json --model medium --compute-type int8

Defaults: language=pt, word_timestamps=True, VAD filter on, model=medium, compute_type=int8.
Output schema matches what import_words.py accepts:
  {"language":"pt","duration":…,"text":…,"words":[{"word","start","end","probability"}],
   "segments":[{"id","start","end","text","words":[…]}]}
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def transcribe(
    source: Path,
    output: Path,
    model_size: str = "medium",
    compute_type: str = "int8",
    language: str = "pt",
    device: str = "cpu",
    vad_filter: bool = True,
) -> dict:
    from faster_whisper import WhisperModel

    source = source.resolve()
    output = output.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if output.exists():
        raise ValueError(f"Refuse to overwrite existing transcript: {output}")

    t0 = time.perf_counter()
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    segments_iter, info = model.transcribe(
        str(source),
        language=language,
        word_timestamps=True,
        vad_filter=vad_filter,
        vad_parameters=dict(min_silence_duration_ms=400),
        beam_size=5,
    )

    segments = []
    words = []
    for i, seg in enumerate(segments_iter):
        seg_words = []
        for w in seg.words or []:
            token = (w.word or "").strip()
            if not token:
                continue
            item = {
                "word": token,
                "start": float(w.start),
                "end": float(w.end),
                "probability": float(getattr(w, "probability", 0.0) or 0.0),
            }
            seg_words.append(item)
            words.append(item)
        segments.append(
            {
                "id": i,
                "start": float(seg.start),
                "end": float(seg.end),
                "text": (seg.text or "").strip(),
                "words": seg_words,
            }
        )
    asr_s = time.perf_counter() - t1

    duration = float(getattr(info, "duration", 0.0) or (words[-1]["end"] if words else 0.0))
    payload = {
        "language": getattr(info, "language", language) or language,
        "language_probability": float(getattr(info, "language_probability", 0.0) or 0.0),
        "duration": duration,
        "text": " ".join(s["text"] for s in segments if s["text"]).strip(),
        "words": words,
        "segments": segments,
        "meta": {
            "engine": "faster-whisper",
            "model": model_size,
            "compute_type": compute_type,
            "device": device,
            "vad_filter": vad_filter,
            "source": str(source),
            "load_seconds": round(load_s, 3),
            "transcribe_seconds": round(asr_s, 3),
            "seconds_per_minute": round((asr_s / duration) * 60, 3) if duration > 0 else None,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(output)
    return payload


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", help="Video or audio file")
    p.add_argument("-o", "--output", required=True, help="Whisper-style JSON path")
    p.add_argument("--model", default="medium", help="Whisper model size (default: medium)")
    p.add_argument("--compute-type", default="int8", help="ctranslate2 compute type (default: int8)")
    p.add_argument("--language", default="pt")
    p.add_argument("--device", default="cpu")
    p.add_argument("--no-vad", action="store_true", help="Disable VAD filter")
    args = p.parse_args()
    result = transcribe(
        Path(args.source),
        Path(args.output),
        model_size=args.model,
        compute_type=args.compute_type,
        language=args.language,
        device=args.device,
        vad_filter=not args.no_vad,
    )
    meta = result["meta"]
    print(
        json.dumps(
            {
                "output": args.output,
                "words": len(result["words"]),
                "segments": len(result["segments"]),
                "duration": result["duration"],
                "language": result["language"],
                **meta,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
