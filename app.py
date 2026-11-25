"""
Garden Harvest Register - Python Application & Local Server

Run this file with Python:
    python app.py

Features:
- Complete dataset of 33 crops across Vegetables, Fruits, Root Crops, and Herbs
- Windows UTF-8 console encoding safe (no charmap UnicodeEncodeErrors)
- Automatic port allocation (finds free port if 8000 is occupied)
- Executive terminal output with category yield distributions and ASCII charts
- Local web server hosting login.html, project.html, and project.js
"""

import http.server
import socketserver
import webbrowser
import os
import sys

# Ensure UTF-8 output on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

HARVEST_DATA = [
    # VEGETABLES
    {"date": "2026-11-23", "crop": "Roma Tomato", "quantity": 14.5, "category": "Vegetables", "bed": "Bed 3"},
    {"date": "2026-11-23", "crop": "Marketmore Cucumber", "quantity": 22.4, "category": "Vegetables", "bed": "Bed 3"},
    {"date": "2026-11-22", "crop": "Calabrese Broccoli", "quantity": 15.2, "category": "Vegetables", "bed": "Bed 4"},
    {"date": "2026-11-22", "crop": "Lacinato Kale", "quantity": 9.4, "category": "Vegetables", "bed": "Bed 4"},
    {"date": "2026-11-22", "crop": "Butterhead Lettuce", "quantity": 8.6, "category": "Vegetables", "bed": "Bed 4"},
    {"date": "2026-11-21", "crop": "Bell Pepper", "quantity": 11.2, "category": "Vegetables", "bed": "Bed 3"},
    {"date": "2026-11-21", "crop": "Black Beauty Eggplant", "quantity": 12.8, "category": "Vegetables", "bed": "Bed 6"},
    {"date": "2026-11-20", "crop": "Sugar Snap Peas", "quantity": 7.4, "category": "Vegetables", "bed": "Bed 1"},
    {"date": "2026-11-19", "crop": "Butternut Squash", "quantity": 28.5, "category": "Vegetables", "bed": "Bed 6"},
    {"date": "2026-11-19", "crop": "Jalapeño Pepper", "quantity": 7.3, "category": "Vegetables", "bed": "Bed 6"},

    # ROOT CROPS
    {"date": "2026-11-23", "crop": "Yukon Gold Potatoes", "quantity": 45.2, "category": "Root Crops", "bed": "Bed 2"},
    {"date": "2026-11-23", "crop": "Jewel Sweet Potato", "quantity": 38.6, "category": "Root Crops", "bed": "Bed 2"},
    {"date": "2026-11-22", "crop": "Yellow Spanish Onion", "quantity": 26.4, "category": "Root Crops", "bed": "Bed 2"},
    {"date": "2026-11-22", "crop": "Nantes Carrots", "quantity": 18.0, "category": "Root Crops", "bed": "Bed 2"},
    {"date": "2026-11-21", "crop": "Chioggia Beetroot", "quantity": 14.8, "category": "Root Crops", "bed": "Bed 4"},
    {"date": "2026-11-21", "crop": "Purple Haze Carrots", "quantity": 11.3, "category": "Root Crops", "bed": "Bed 2"},
    {"date": "2026-11-20", "crop": "Hardneck Garlic", "quantity": 8.9, "category": "Root Crops", "bed": "Bed 1"},
    {"date": "2026-11-20", "crop": "Red Radish", "quantity": 5.5, "category": "Root Crops", "bed": "Bed 2"},

    # FRUITS
    {"date": "2026-11-23", "crop": "Sugar Baby Watermelon", "quantity": 34.0, "category": "Fruits", "bed": "Bed 6"},
    {"date": "2026-11-23", "crop": "Cantaloupe Melon", "quantity": 19.5, "category": "Fruits", "bed": "Bed 6"},
    {"date": "2026-11-22", "crop": "Crimson Seedless Grapes", "quantity": 16.2, "category": "Fruits", "bed": "Bed 5"},
    {"date": "2026-11-22", "crop": "Meyer Lemon", "quantity": 14.0, "category": "Fruits", "bed": "Bed 5"},
    {"date": "2026-11-21", "crop": "Albion Strawberry", "quantity": 6.8, "category": "Fruits", "bed": "Bed 5"},
    {"date": "2026-11-20", "crop": "Triple Crown Blackberry", "quantity": 5.8, "category": "Fruits", "bed": "Bed 5"},
    {"date": "2026-11-19", "crop": "Blueberry", "quantity": 4.6, "category": "Fruits", "bed": "Bed 5"},

    # HERBS
    {"date": "2026-11-23", "crop": "Lemongrass", "quantity": 6.0, "category": "Herbs", "bed": "Bed 6"},
    {"date": "2026-11-23", "crop": "Italian Parsley", "quantity": 5.6, "category": "Herbs", "bed": "Bed 1"},
    {"date": "2026-11-22", "crop": "Peppermint", "quantity": 4.2, "category": "Herbs", "bed": "Bed 1"},
    {"date": "2026-11-22", "crop": "Coriander / Cilantro", "quantity": 4.1, "category": "Herbs", "bed": "Bed 4"},
    {"date": "2026-11-21", "crop": "Greek Oregano", "quantity": 3.4, "category": "Herbs", "bed": "Bed 1"},
    {"date": "2026-11-21", "crop": "Genovese Basil", "quantity": 3.2, "category": "Herbs", "bed": "Bed 1"},
    {"date": "2026-11-20", "crop": "Garden Thyme", "quantity": 2.8, "category": "Herbs", "bed": "Bed 1"},
    {"date": "2026-11-20", "crop": "Rosemary", "quantity": 2.1, "category": "Herbs", "bed": "Bed 1"},
]

def make_bar(percent, width=14):
    filled = int(round((percent / 100.0) * width))
    return "#" * filled + "-" * (width - filled)

def print_summary():
    total_yield = sum(item["quantity"] for item in HARVEST_DATA)
    total_crops = len(HARVEST_DATA)

    cat_stats = {}
    for item in HARVEST_DATA:
        cat = item["category"]
        if cat not in cat_stats:
            cat_stats[cat] = {"count": 0, "yield": 0.0}
        cat_stats[cat]["count"] += 1
        cat_stats[cat]["yield"] += item["quantity"]

    bed_stats = {}
    for item in HARVEST_DATA:
        bed = item["bed"]
        bed_stats[bed] = bed_stats.get(bed, 0.0) + item["quantity"]

    top_bed = max(bed_stats.items(), key=lambda x: x[1])

    print("\n" + "=" * 70)
    print("  COMMUNITY GARDEN HARVEST REGISTER - EXECUTIVE REPORT")
    print("=" * 70)

    print("\n[HARVEST KPI SUMMARY]")
    print(f"  * Total Yield Recorded:  {total_yield:.1f} kg across 6 garden plots")
    print(f"  * Crop Varieties Logged: {total_crops} varieties across 4 categories")
    print(f"  * Top Producing Plot:    {top_bed[0]} ({top_bed[1]:.1f} kg recorded)")
    print(f"  * Quality Grade Rating:  93.9% Prime (Grade A / Organic)")

    print("\n[CATEGORY DISTRIBUTION BREAKDOWN]")
    print(f"  {'Category':<14} | {'Count':<5} | {'Yield (kg)':<10} | {'Ratio':<6} | {'Distribution':<16}")
    print("  " + "-" * 62)

    sorted_cats = sorted(cat_stats.items(), key=lambda x: x[1]["yield"], reverse=True)
    for cat, data in sorted_cats:
        ratio = (data["yield"] / total_yield) * 100
        bar = make_bar(ratio, 14)
        print(f"  {cat:<14} | {data['count']:<5d} | {data['yield']:>8.1f} kg | {ratio:>5.1f}% | [{bar}]")

    print("\n[BED PRODUCTIVITY]")
    for bed, b_yield in sorted(bed_stats.items(), key=lambda x: x[1], reverse=True):
        b_ratio = (b_yield / total_yield) * 100
        bar = make_bar(b_ratio, 16)
        print(f"  {bed:<6} : {b_yield:>6.1f} kg ({b_ratio:4.1f}%) [{bar}]")
    print("=" * 70)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/login.html")
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True

def get_free_port(start_port=8000):
    for p in range(start_port, start_port + 20):
        try:
            with ReusableServer(("", p), CustomHandler) as test_server:
                return p
        except OSError:
            continue
    return start_port

def main():
    print_summary()
    port = get_free_port(DEFAULT_PORT)
    url = f"http://localhost:{port}/login.html"
    project_url = f"http://localhost:{port}/project.html"

    print(f"\n>> Local Web Server ready at: {url}")
    print(f">> Direct Dashboard link:     {project_url}\n")
    print("Default demo accounts:")
    print("  * Username: admin   | Password: garden2026 (Administrator)")
    print("  * Username: akarsh  | Password: harvest123 (Lead Harvester)")
    print("  * Or click 'Continue as Guest' on the login screen.\n")
    print("Press Ctrl+C in this terminal to stop the server.\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        with ReusableServer(("", port), CustomHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
