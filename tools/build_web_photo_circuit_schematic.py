from pathlib import Path
from urllib.parse import quote
import zipfile

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "figures" / "web_assets"
OUT = ROOT / "figures" / "myosense_web_photo_circuit_schematic.png"
W, H = 3200, 1600

SOURCES = {
    "bioamp.png": "https://docs.upsidedownlabs.tech/_images/muscle-bioamp-candy-front.png",
    "udl_kit.png": "https://docs.upsidedownlabs.tech/_images/kit-contents3.png",
    "esp32.png": "https://epartners.co.nz/cdn/shop/files/esp32-s3-n16r8-development-board-610717.png?v=1748416924",
    "charger.jpg": "https://cdn3.botland.store/img/art/inne/16979_6.jpg",
    "boost.jpg": "https://dfimg.dfrobot.com/enshop/image/data/FIT0471/1.jpg",
    "battery.jpg": "https://zaitronics.com.au/cdn/shop/files/1000mah503450.jpg?v=1745219121%26width=1000",
}

NAVY = "#173247"
TEXT = "#2C414F"
MUTED = "#5F737F"
PANEL = "#FBFCFD"
BORDER = "#BCC9D1"
BLUE = "#1677A8"
RED = "#BF573A"
GROUND = "#3B464C"
PALE_BLUE = "#EFF6F9"
PALE_RED = "#FFF4EF"
WHITE = "#FFFFFF"


def get_font(size, bold=False):
    file = Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf")
    if file.exists():
        return ImageFont.truetype(str(file), size)
    return ImageFont.load_default()


def download_assets():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (compatible; MyoSense-figure/1.0)"
    for filename, url in SOURCES.items():
        target = ASSET_DIR / filename
        if target.exists() and target.stat().st_size > 1000:
            continue
        response = session.get(url, timeout=45)
        response.raise_for_status()
        if not response.headers.get("content-type", "").startswith("image/"):
            raise ValueError(f"Expected an image for {url}")
        target.write_bytes(response.content)


def crop_assets():
    bioamp = Image.open(ASSET_DIR / "bioamp.png").convert("RGBA")
    esp = Image.open(ASSET_DIR / "esp32.png").convert("RGBA")
    charger = Image.open(ASSET_DIR / "charger.jpg").convert("RGBA")
    boost = Image.open(ASSET_DIR / "boost.jpg").convert("RGBA")
    battery = Image.open(ASSET_DIR / "battery.jpg").convert("RGBA")
    kit = Image.open(ASSET_DIR / "udl_kit.png").convert("RGBA")

    # The official kit image places the gel electrode beside the cable and sensor.
    electrode = kit.crop((1370, 430, 1590, 670))
    esp_board = esp.crop((45, 565, 1035, 1050)).rotate(180, expand=True)
    boost_board = boost.crop((210, 90, 690, 535))

    assets = {
        "bioamp": bioamp,
        "electrode": electrode,
        "esp32": esp_board,
        "charger": charger,
        "boost": boost_board,
        "battery": battery,
    }
    return assets


def text(draw, xy, value, size=22, color=TEXT, bold=False, anchor=None):
    draw.text(xy, value, fill=color, font=get_font(size, bold), anchor=anchor)


def panel(draw, box, radius=24, fill=PANEL, outline=BORDER, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def label(draw, center, value, size=19, color=TEXT):
    font = get_font(size, True)
    box = draw.textbbox((0, 0), value, font=font)
    width = box[2] - box[0] + 26
    height = box[3] - box[1] + 15
    x = int(center[0] - width / 2)
    y = int(center[1] - height / 2)
    draw.rounded_rectangle((x, y, x + width, y + height), radius=7, fill=WHITE)
    draw.text((center[0], center[1]), value, fill=color, font=font, anchor="mm")


def line(draw, points, color, width=5, dash=False):
    if not dash:
        draw.line(points, fill=color, width=width, joint="curve")
        return
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        dx, dy = x2 - x1, y2 - y1
        length = max(1, int((dx * dx + dy * dy) ** 0.5))
        ux, uy = dx / length, dy / length
        for start in range(0, length, 26):
            end = min(start + 14, length)
            draw.line((x1 + ux * start, y1 + uy * start, x1 + ux * end, y1 + uy * end), fill=color, width=width)


def arrow(draw, start, end, color, width=5):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    angle = __import__("math").atan2(y2 - y1, x2 - x1)
    size = 17
    left = (x2 - size * __import__("math").cos(angle - 0.45), y2 - size * __import__("math").sin(angle - 0.45))
    right = (x2 - size * __import__("math").cos(angle + 0.45), y2 - size * __import__("math").sin(angle + 0.45))
    draw.polygon((end, left, right), fill=color)


def photo(draw, canvas, image, box, pad=18):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=15, fill=WHITE, outline="#D7E0E5", width=2)
    area = (x1 + pad, y1 + pad, x2 - pad, y2 - pad)
    fitted = ImageOps.contain(image, (area[2] - area[0], area[3] - area[1]))
    px = area[0] + (area[2] - area[0] - fitted.width) // 2
    py = area[1] + (area[3] - area[1] - fitted.height) // 2
    if fitted.mode == "RGBA":
        canvas.alpha_composite(fitted, (px, py))
    else:
        canvas.paste(fitted, (px, py))


def card(draw, box, title, subtitle=None):
    panel(draw, box, radius=22, fill=WHITE, outline=BORDER, width=3)
    x1, y1, x2, _ = box
    text(draw, ((x1 + x2) // 2, y1 + 27), title, 25, NAVY, True, "mt")
    if subtitle:
        text(draw, ((x1 + x2) // 2, y1 + 60), subtitle, 18, MUTED, False, "mt")


def draw_resistor_h(draw, x1, x2, y, color=RED):
    body_start, body_end = x1 + 24, x2 - 24
    draw.line((x1, y, body_start, y), fill=color, width=5)
    draw.line((body_end, y, x2, y), fill=color, width=5)
    points = [(body_start, y)]
    step = (body_end - body_start) / 8
    for i in range(1, 8):
        points.append((body_start + i * step, y - (20 if i % 2 else -20)))
    points.append((body_end, y))
    draw.line(points, fill=color, width=5, joint="curve")


def draw_resistor_v(draw, x, y1, y2, color=GROUND):
    body_start, body_end = y1 + 20, y2 - 20
    draw.line((x, y1, x, body_start), fill=color, width=5)
    draw.line((x, body_end, x, y2), fill=color, width=5)
    points = [(x, body_start)]
    step = (body_end - body_start) / 8
    for i in range(1, 8):
        points.append((x + (20 if i % 2 else -20), body_start + i * step))
    points.append((x, body_end))
    draw.line(points, fill=color, width=5, joint="curve")


def draw_usb_icon(draw, x, y, title, subtitle):
    panel(draw, (x, y, x + 270, y + 220), radius=20, fill=WHITE, outline=BORDER, width=3)
    draw.rounded_rectangle((x + 100, y + 35, x + 170, y + 115), radius=12, outline=NAVY, width=5, fill="#F4F7F9")
    draw.line((x + 118, y + 51, x + 152, y + 51), fill=NAVY, width=4)
    draw.line((x + 118, y + 99, x + 152, y + 99), fill=NAVY, width=4)
    text(draw, (x + 135, y + 135), title, 22, NAVY, True, "mt")
    text(draw, (x + 135, y + 169), subtitle, 17, MUTED, False, "mt")


def draw_diagram():
    assets = crop_assets()
    canvas = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)

    text(draw, (W // 2, 25), "MyoSense · photo-annotated circuit schematic", 46, NAVY, True, "mt")
    text(draw, (W // 2, 78), "Single-channel sEMG acquisition, battery power and GPIO1 voltage sensing", 25, MUTED, False, "mt")

    panel(draw, (45, 125, 3155, 660), radius=22)
    text(draw, (90, 150), "A   SIGNAL ACQUISITION", 26, NAVY, True, "lt")

    card(draw, (90, 215, 555, 600), "J1 · ELECTRODE SET", "3 contacts; use labeled lead functions")
    photo(draw, canvas, assets["electrode"], (125, 300, 520, 475), 8)
    text(draw, (322, 500), "IN+  ·  IN−  ·  REF", 23, TEXT, True, "mt")
    text(draw, (322, 538), "IN+/IN− on target muscle; REF at reference site", 16, MUTED, False, "mt")

    card(draw, (690, 215, 1270, 600), "U1 · EMG FRONT END", "Photographed board is representative; verify exact revision")
    photo(draw, canvas, assets["bioamp"], (745, 300, 1215, 475), 5)
    text(draw, (980, 500), "IN+ / IN− / REF   →   U1 electrode connector", 17, TEXT, True, "mt")
    text(draw, (980, 535), "VCC · GND · OUT at board power/signal pins", 17, MUTED, False, "mt")
    text(draw, (980, 565), "If Candy: ×2420, 72–720 Hz (verify model)", 16, MUTED, False, "mt")

    card(draw, (1450, 215, 2220, 600), "U2 · ESP32-S3 N16R8", "Representative N16R8 development-board photo")
    photo(draw, canvas, assets["esp32"], (1480, 295, 1800, 565), 4)
    text(draw, (1830, 360), "GPIO4 / ADC1_CH3  ← EMG OUT", 20, BLUE, True, "lm")
    text(draw, (1830, 416), "3V3 rail  → EMG VCC", 20, RED, True, "lm")
    text(draw, (1830, 472), "GND  ↔ EMG GND", 20, GROUND, True, "lm")
    text(draw, (1830, 528), "GPIO1 / ADC1_CH0  ← divider midpoint", 19, BLUE, True, "lm")
    text(draw, (1830, 564), "ADC pin limit: 0–3.3 V", 17, "#963D2C", True, "lm")

    card(draw, (2525, 270, 3020, 555), "BLE LINK", "No electrical wire to the phone")
    draw.rounded_rectangle((2710, 330, 2835, 485), radius=20, outline=NAVY, width=5, fill="#F4F7F9")
    draw.line((2740, 455, 2805, 455), fill=NAVY, width=4)
    text(draw, (2772, 510), "Phone / browser meter", 19, TEXT, False, "mt")

    # Electrode input nets.
    for y, name in ((365, "IN+"), (420, "IN−"), (475, "REF")):
        draw.ellipse((540, y - 8, 556, y + 8), fill=WHITE, outline=BLUE, width=4)
        line(draw, ((556, y), (690, y)), BLUE, 5)
        label(draw, (623, y - 16), name, 17, BLUE)

    # Front-end output, supply and common ground.
    for y, color, name in ((365, BLUE, "OUT → GPIO4"), (420, RED, "3V3 → VCC"), (475, GROUND, "GND → GND")):
        line(draw, ((1270, y), (1450, y)), color, 5)
        draw.ellipse((1442, y - 8, 1458, y + 8), fill=WHITE, outline=color, width=4)
        label(draw, (1360, y - 18), name, 17, color)

    line(draw, ((2220, 410), (2525, 410)), MUTED, 4, dash=True)
    label(draw, (2372, 390), "BLE 5", 17, MUTED)

    text(draw, (85, 632), "Signal chain: electrodes → U1 analog front end → U2 GPIO4 ADC. Firmware samples at 2 ksample/s and streams readings by BLE.", 18, MUTED, False, "lm")

    panel(draw, (45, 685, 3155, 1535), radius=22)
    text(draw, (90, 712), "B   POWER, CHARGING AND BATTERY-VOLTAGE DIVIDER", 26, NAVY, True, "lt")

    draw_usb_icon(draw, 85, 800, "USB-C 5 V", "charger input only")
    card(draw, (455, 790, 910, 1090), "U3 · HW-373", "TP4056 + protection board")
    photo(draw, canvas, assets["charger"], (480, 860, 720, 1065), 3)
    text(draw, (740, 885), "B+ / B−", 17, NAVY, True, "lm")
    text(draw, (740, 925), "OUT+", 17, RED, True, "lm")
    text(draw, (740, 965), "OUT−", 17, GROUND, True, "lm")
    text(draw, (740, 1025), "USB-C IN", 16, MUTED, True, "lm")

    card(draw, (1010, 800, 1410, 1070), "BT1 · 1S CELL", "Representative LiPo pouch battery")
    photo(draw, canvas, assets["battery"], (1040, 870, 1380, 1020), 5)
    text(draw, (1210, 1032), "3.7 V nominal · 1000 mAh", 17, TEXT, True, "mt")

    card(draw, (1510, 790, 1955, 1090), "U4 · HW-106", "Installed 3.7 V → 5 V USB boost")
    photo(draw, canvas, assets["boost"], (1535, 860, 1805, 1055), 2)
    text(draw, (1830, 900), "VIN+", 17, RED, True, "lm")
    text(draw, (1830, 940), "VIN−", 17, GROUND, True, "lm")
    text(draw, (1830, 995), "USB-A 5 V", 17, NAVY, True, "lm")
    text(draw, (1830, 1033), "GND", 17, GROUND, True, "lm")
    text(draw, (1732, 1070), "Photo is a representative boost board, not the HW-106 itself.", 15, MUTED, False, "mt")

    card(draw, (2040, 800, 2450, 1070), "U2 POWER INPUT", "Same ESP32 board as panel A")
    draw.rounded_rectangle((2120, 865, 2370, 935), radius=11, outline=NAVY, width=4, fill="#F4F7F9")
    draw.rectangle((2185, 879, 2305, 920), fill="#D9E2E7", outline=NAVY, width=3)
    text(draw, (2245, 957), "USB-A → USB-C cable", 18, TEXT, True, "mt")
    text(draw, (2245, 1000), "regulated 5 V to board", 17, MUTED, False, "mt")

    panel(draw, (2550, 790, 3105, 1090), radius=18, fill=PALE_BLUE, outline="#B4CCD9", width=3)
    text(draw, (2580, 820), "POWER-NET NOTES", 21, NAVY, True, "lm")
    text(draw, (2580, 862), "HW-373 B+/B− → cell +/−", 18, TEXT, False, "lm")
    text(draw, (2580, 902), "HW-373 OUT+/OUT− → HW-106 VIN+/VIN−", 17, TEXT, False, "lm")
    text(draw, (2580, 946), "Boost USB-A 5 V/GND → ESP32 USB-C", 17, TEXT, False, "lm")
    text(draw, (2580, 994), "HW-373 OUT is battery voltage, not 5 V.", 17, "#963D2C", True, "lm")
    text(draw, (2580, 1035), "Do not also connect PC USB while boost powers U2.", 16, "#963D2C", True, "lm")

    # USB charge input to the TP4056 board.
    line(draw, ((355, 890), (455, 890)), RED, 5)
    line(draw, ((355, 950), (455, 950)), GROUND, 5)
    label(draw, (405, 875), "5 V", 16, RED)
    label(draw, (405, 966), "GND", 16, GROUND)

    # Battery terminals from HW-373 B pads.
    line(draw, ((910, 890), (1010, 890)), RED, 5)
    line(draw, ((910, 950), (1010, 950)), GROUND, 5)
    label(draw, (960, 873), "B+", 16, RED)
    label(draw, (960, 970), "B−", 16, GROUND)

    # Protected battery output to boost input. Net labels also feed the divider below.
    line(draw, ((910, 925), (960, 925), (960, 1120), (1470, 1120), (1470, 900), (1510, 900)), RED, 5)
    line(draw, ((910, 965), (990, 965), (990, 1160), (1490, 1160), (1490, 940), (1510, 940)), GROUND, 5)
    label(draw, (1190, 1100), "BATT+ = HW-373 OUT+ = U4 VIN+", 17, RED)
    label(draw, (1190, 1182), "BATT− = HW-373 OUT− = U4 VIN− / common GND", 16, GROUND)

    # Boost output to the ESP32 USB-C power input.
    line(draw, ((1955, 900), (2040, 900)), RED, 5)
    line(draw, ((1955, 940), (2040, 940)), GROUND, 5)
    label(draw, (1997, 884), "5 V", 16, RED)
    label(draw, (1997, 956), "GND", 16, GROUND)

    # User-installed battery sense divider, across the protected cell-voltage output.
    panel(draw, (90, 1230, 3105, 1435), radius=18, fill="#FCFDFE", outline="#8197A3", width=3)
    text(draw, (125, 1255), "BATTERY SENSE · TWO EQUAL 68 kΩ RESISTORS", 22, NAVY, True, "lm")
    text(draw, (125, 1305), "HW-373 OUT+ / BATT+", 18, RED, True, "lm")
    line(draw, ((125, 1350), (400, 1350)), RED, 5)
    draw_resistor_h(draw, 400, 680, 1350, RED)
    text(draw, (540, 1317), "R1 = 68 kΩ", 17, TEXT, True, "mm")
    line(draw, ((680, 1350), (900, 1350)), RED, 5)
    draw.ellipse((891, 1341, 909, 1359), fill=BLUE)
    line(draw, ((900, 1350), (1730, 1350)), BLUE, 5)
    text(draw, (1780, 1350), "GPIO1 / ADC1_CH0 on U2", 19, BLUE, True, "lm")
    draw_resistor_v(draw, 900, 1350, 1410, GROUND)
    text(draw, (955, 1380), "R2 = 68 kΩ", 17, TEXT, True, "lm")
    line(draw, ((900, 1410), (900, 1417)), GROUND, 5)
    draw.line((870, 1417, 930, 1417), fill=GROUND, width=5)
    draw.line((879, 1424, 921, 1424), fill=GROUND, width=5)
    draw.line((889, 1431, 911, 1431), fill=GROUND, width=5)
    text(draw, (1110, 1417), "HW-373 OUT− / ESP32 GND (common)", 17, GROUND, False, "lm")
    text(draw, (2100, 1310), "VGPIO1 = Vcell / 2", 19, NAVY, True, "lm")
    text(draw, (2100, 1350), "At 4.2 V full cell: 2.1 V at GPIO1", 17, TEXT, False, "lm")
    text(draw, (2100, 1390), "Tap HW-373 OUT+, never the boost's USB-A 5 V.", 17, "#963D2C", True, "lm")
    text(draw, (2100, 1420), "BLE firmware divider scale = 2.0.", 16, MUTED, False, "lm")

    panel(draw, (90, 1455, 3105, 1515), radius=12, fill=PALE_RED, outline="#E3B8A7", width=2)
    text(draw, (120, 1485), "BODY-RECORDING SAFETY: run from the battery only. Disconnect charger and mains-connected computer USB; verify battery polarity, 5 V boost output and GPIO voltage before use.", 17, "#963D2C", True, "lm")

    text(draw, (90, 1563), "Web-image credits: Upside Down Labs (BioAmp/electrode kit), ePartners (ESP32-S3 N16R8), Botland (HW-373), DFRobot (representative boost image), Zaitronics (representative 1000 mAh cell).", 14, MUTED, False, "lm")
    text(draw, (90, 1587), "Exact board revisions and the battery connector are not all confirmed; photos are illustrative. Wiring labels, HW-106 connections and the 68 kΩ divider follow the documented project design.", 14, MUTED, False, "lm")

    canvas.convert("RGB").save(OUT, quality=95)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    download_assets()
    draw_diagram()
