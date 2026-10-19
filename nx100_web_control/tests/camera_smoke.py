"""MOCK-only camera UI checks, including original-pixel mapping and no robot sends."""

import json
import os
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

URL = os.environ.get("NX100_TEST_URL", "http://127.0.0.1:8001")
with urlopen(URL + "/api/config") as response:
    if json.load(response)["mode"] != "MOCK":
        raise RuntimeError("Camera QA requires isolated MOCK mode")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    errors, requests, conversions = [], [], []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def request_seen(request):
        if request.method == "POST":
            requests.append(request.url)
            if request.url.endswith("/api/vision/pixel-to-base"):
                conversions.append(request.post_data_json)

    page.on("request", request_seen)
    page.goto(URL + "/camera")
    expect(page.locator("#visionMode")).to_have_text("MOCK")
    expect(page.locator("#quality")).to_contain_text("needs_review")
    expect(page.locator("#quality")).to_contain_text("63.97 mm")
    assert not requests, "Camera page must not auto-connect hardware"
    page.click("#findCamera")
    page.click("#openCamera")
    expect(page.locator("#emptyCamera")).to_be_hidden(timeout=7000)
    expect(page.locator("#frameInfo")).to_contain_text("5472 × 3648 raw")
    bounds = page.locator("#cameraCanvas").bounding_box()
    page.locator("#cameraCanvas").click(
        position={"x": bounds["width"] * 0.5, "y": bounds["height"] * 0.5}
    )
    expect(page.locator("#pixelValue")).to_contain_text("u ")
    expect(page.locator("#pointMessage")).to_contain_text("Nhập Z")
    assert not conversions, "Do not assume Z=0 for an unspecified work plane"
    page.locator("#planeZ").fill("100")
    page.locator("#planeZ").press("Enter")
    expect(page.locator("#baseZ")).to_have_text("100.000")
    expect(page.locator("#pointPhase")).to_have_text("MOCK ESTIMATE")
    assert abs(conversions[-1]["u"] - 2736) <= 1
    assert abs(conversions[-1]["v"] - 1824) <= 1
    assert conversions[-1]["plane_z_mm"] == 100
    page.locator("#planeZ").fill("250")
    expect(page.locator("#baseZ")).to_have_text("—")
    page.click("#convertPoint")
    expect(page.locator("#baseZ")).to_have_text("250.000")
    assert not any("/api/move/" in url or url.endswith("/api/connect") for url in requests)
    evidence = Path(__file__).resolve().parents[1] / "qa"
    page.screenshot(path=str(evidence / "camera-desktop.png"), full_page=True)
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=str(evidence / "camera-mobile.png"), full_page=True)
    page.click("#closeCamera")
    expect(page.locator("#emptyCamera")).to_be_visible()
    assert not errors, errors
    browser.close()
    print(
        "Camera browser passed: raw pixel mapping; explicit Z; matrix conversion; quality warning; no robot commands; responsive; no JS errors."
    )
