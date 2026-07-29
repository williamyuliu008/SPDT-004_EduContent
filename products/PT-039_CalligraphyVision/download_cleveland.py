# -*- coding: utf-8 -*-
"""
PT-039 Cleveland Museum of Art Calligraphy Downloader
Source: openaccess-api.clevelandart.org (CC0)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
import time

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"D:\92_products\PT-039_AiIllustration_Exploration\真实碑帖素材库"

ARTWORKS = [
    {
        "accession": "1961.421.2",
        "label": "Song Lizong Cursive Script - Album leaf (绢本) 1256",
        "target_dir": "10_SouthernSong_SongLizong",
        "web_url": "https://openaccess-cdn.clevelandart.org/1961.421.2/1961.421.2_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/1961.421.2/1961.421.2_print.jpg",
        "metadata_url": "https://clevelandart.org/art/1961.421.2",
        "source": "Cleveland Museum of Art, CC0",
    },
    {
        "accession": "2025.192",
        "label": "Zhu Yunming Cursive Script - Handscroll 1523",
        "target_dir": "11_Ming_ZhuYunming",
        "web_url": "https://openaccess-cdn.clevelandart.org/2025.192/2025.192_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/2025.192/2025.192_print.jpg",
        "metadata_url": "https://clevelandart.org/art/2025.192",
        "source": "Cleveland Museum of Art, CC0",
    },
    {
        "accession": "2001.42",
        "label": "Tiebao Running Script - Handscroll 1811 (王勃·滕王阁序)",
        "target_dir": "12_Qing_Tiebao",
        "web_url": "https://openaccess-cdn.clevelandart.org/2001.42/2001.42_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/2001.42/2001.42_print.jpg",
        "metadata_url": "https://clevelandart.org/art/2001.42",
        "source": "Cleveland Museum of Art, CC0",
    },
    {
        "accession": "2003.353",
        "label": "Tsunonoyama Dōsō / Yueshan Large Calligraphy - Handscroll c.1660 (Japanese 黄檗 style, proxy for 张旭/怀素 visual reference)",
        "target_dir": "13_Qing_Yueshan",
        "web_url": "https://openaccess-cdn.clevelandart.org/2003.353/2003.353_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/2003.353/2003.353_print.jpg",
        "metadata_url": "https://clevelandart.org/art/2003.353",
        "source": "Cleveland Museum of Art, CC0",
        "note": "Japanese Buddhist 黄檗 calligrapher; used as visual style proxy (圆转丰厚/草书韵味) for Tang masters comparison cards",
    },
    {
        "accession": "2003.354",
        "label": "Tsunonoyama Dōsō / Yueshan Alternative View - Handscroll c.1660",
        "target_dir": "14_Qing_Yueshan2",
        "web_url": "https://openaccess-cdn.clevelandart.org/2003.354/2003.354_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/2003.354/2003.354_print.jpg",
        "metadata_url": "https://clevelandart.org/art/2003.354",
        "source": "Cleveland Museum of Art, CC0",
    },
    {
        "accession": "1998.169",
        "label": "Wen Zhengming Running-Standard Script - Handscroll c.1525 (文徵明 行楷, proxy for 欧阳询 visual reference)",
        "target_dir": "15_Ming_WenZhengming",
        "web_url": "https://openaccess-cdn.clevelandart.org/1998.169/1998.169_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/1998.169/1998.169_print.jpg",
        "metadata_url": "https://clevelandart.org/art/1998.169",
        "source": "Cleveland Museum of Art, CC0",
        "note": "Ming dynasty 文徵明; used as visual style proxy (工整清秀/行楷) for Tang 楷书 masters comparison cards",
    },
    {
        "accession": "2004.65",
        "label": "Chen Jiru Cursive Script - 金粟山藏经纸 c.1500s (proxy for 孙过庭 书谱 visual reference)",
        "target_dir": "16_Ming_ChenJiru",
        "web_url": "https://openaccess-cdn.clevelandart.org/2004.65/2004.65_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/2004.65/2004.65_print.jpg",
        "metadata_url": "https://clevelandart.org/art/2004.65",
        "source": "Cleveland Museum of Art, CC0",
        "note": "Ming dynasty; used as visual style proxy (精到工稳/草书面貌) for Tang 草书 masters comparison",
    },
    {
        "accession": "1978.69",
        "label": "Song Lizong Cursive Script - Album leaf on silk 1259 (补充款)",
        "target_dir": "17_SouthernSong_SongLizong2",
        "web_url": "https://openaccess-cdn.clevelandart.org/1978.69/1978.69_web.jpg",
        "print_url": "https://openaccess-cdn.clevelandart.org/1978.69/1978.69_print.jpg",
        "metadata_url": "https://clevelandart.org/art/1978.69",
        "source": "Cleveland Museum of Art, CC0",
    },
]


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"  [DIR] created: {path}")


def download(url: str, dest: str, timeout: int = 45) -> bool:
    """Returns True if file exists or downloaded successfully."""
    if os.path.exists(dest):
        size_mb = os.path.getsize(dest) / 1024 / 1024
        print(f"  [SKIP] already exists: {os.path.basename(dest)} ({size_mb:.1f}MB)")
        return True

    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                },
            )
            print(f"  [DOWN] {url}")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()

            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)

            size_mb = len(data) / 1024 / 1024
            print(f"  [DONE] {os.path.basename(dest)} ({size_mb:.2f}MB) -> {dest}")
            return True

        except Exception as exc:
            print(f"  [ERR]  attempt {attempt+1}/3 failed: {exc}")
            if attempt < 2:
                wait = (attempt + 1) * 8
                print(f"  [WAIT] retrying in {wait}s...")
                time.sleep(wait)

    return False


def main():
    print("=" * 65)
    print("PT-039 Cleveland Museum Calligraphy Downloader")
    print("Source: openaccess-api.clevelandart.org  |  License: CC0")
    print("=" * 65)

    results = []

    for item in ARTWORKS:
        acc = item["accession"]
        label = item["label"]
        target_dir = os.path.join(BASE_DIR, item["target_dir"])

        print(f"\n==> [{acc}] {label}")
        ensure_dir(target_dir)

        # 1) Download WEB version (900px, fast)
        web_name = f"{acc}_web.jpg"
        web_path = os.path.join(target_dir, web_name)
        web_ok = download(item["web_url"], web_path, timeout=30)
        item["web_downloaded"] = web_ok
        item["web_path"] = web_path

        # 2) Download PRINT version (3400px, if web succeeded)
        if web_ok:
            print("  --- downloading high-res (print 3400px) ---")
            print_name = f"{acc}_print.jpg"
            print_path = os.path.join(target_dir, print_name)
            print_ok = download(item["print_url"], print_path, timeout=60)
            item["print_downloaded"] = print_ok
            item["print_path"] = print_path

        time.sleep(2)

    # Summary
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    for item in ARTWORKS:
        w = "[WEB]" if item.get("web_downloaded") else "[---]"
        p = "[PRINT]" if item.get("print_downloaded") else "[-----]"
        print(f"  {w} {p}  {item['accession']}  {item['label']}")
        results.append({
            "accession": item["accession"],
            "label": item["label"],
            "target_dir": item["target_dir"],
            "web_url": item["web_url"],
            "print_url": item.get("print_url"),
            "web_path": item.get("web_path"),
            "print_path": item.get("print_path"),
            "web_downloaded": item.get("web_downloaded"),
            "print_downloaded": item.get("print_downloaded"),
            "source": item["source"],
            "license": "CC0",
            "metadata_url": item["metadata_url"],
        })

    # Save metadata
    meta_file = os.path.join(BASE_DIR, "metadata", "cleveland_downloads.json")
    os.makedirs(os.path.dirname(meta_file), exist_ok=True)
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nMetadata saved: {meta_file}")


if __name__ == "__main__":
    main()
