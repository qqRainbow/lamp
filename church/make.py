# Makes Lamp's church materials: the QR code, a printable A4 poster (PDF) and a 16:9 slide (PNG).
# If Lamp moves to a new address, change URL below and run:  py church/make.py
# Needs the "segno" package (py -m pip install segno) and Microsoft Edge.
import pathlib, re, subprocess, tempfile
import segno

URL = "https://qqrainbow.github.io/lamp/"
HERE = pathlib.Path(__file__).parent
OUT = HERE / "print"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

OUT.mkdir(exist_ok=True)
qr = segno.make(URL, error="q")  # "q": still scans with about a quarter of the code smudged or covered
qr.save(OUT / "lamp-qr.svg", scale=10, border=4, dark="#111827", light="#ffffff")
qr.save(OUT / "lamp-qr.png", scale=24, border=4, dark="#111827", light="#ffffff")
inline = qr.svg_inline(scale=1, border=0, dark="#111827", light=None)
# Let the code scale to fill its box: give it a viewBox in place of a fixed size.
n = qr.symbol_size(border=0)[0]
inline = re.sub(r'\s(width|height)="\d+"', "", inline, count=2).replace("<svg", f'<svg viewBox="0 0 {n} {n}" shape-rendering="crispEdges"', 1)
short = URL.removeprefix("https://").rstrip("/")

def fill(name):
    page = (HERE / name).read_text(encoding="utf-8").replace("{{QR}}", inline).replace("{{URL_SHORT}}", short)
    path = pathlib.Path(tempfile.gettempdir()) / ("lamp-" + name)
    path.write_text(page, encoding="utf-8")
    return path.as_uri()

def edge(*args):
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
                        "--virtual-time-budget=4000", "--hide-scrollbars", *args], check=True, capture_output=True, timeout=90)

edge(f"--print-to-pdf={OUT / 'lamp-poster.pdf'}", "--no-pdf-header-footer", fill("poster.html"))
edge(f"--screenshot={OUT / 'lamp-slide.png'}", "--window-size=1920,1080", fill("slide.html"))
print("Made:", *sorted(p.name for p in OUT.iterdir()))
