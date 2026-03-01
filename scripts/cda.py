from bs4 import BeautifulSoup
import re

def merge_pixels_to_rects(pixels_coords):
    """
    Algoritmo Greedy per fondere pixel adiacenti in rettangoli.
    """
    rects = []
    # Usiamo un set per una ricerca rapida dei pixel disponibili
    unvisited = set(pixels_coords)
    
    while unvisited:
        # Prendi il primo pixel disponibile (top-left)
        x, y = min(unvisited, key=lambda p: (p[1], p[0]))
        
        # Estendi il rettangolo in larghezza (W)
        w = 1
        while (x + w, y) in unvisited:
            w += 1
            
        # Estendi il rettangolo in altezza (H)
        h = 1
        while True:
            # Controlla se l'intera riga successiva di larghezza W è presente
            all_row_present = True
            for dx in range(w):
                if (x + dx, y + h) not in unvisited:
                    all_row_present = False
                    break
            if all_row_present:
                h += 1
            else:
                break
        
        # Abbiamo trovato un rettangolo di W x H. Rimuovilo dai non visitati.
        for dy in range(h):
            for dx in range(w):
                unvisited.remove((x + dx, y + dy))
        
        rects.append((x, y, w, h))
    return rects

# Carica il file
with open("diagramma_automatizzato.html", "r") as f:
    soup = BeautifulSoup(f, "html.parser")

# Raggruppa coordinate per colore
color_groups = {}
for px in soup.find_all("div", class_="p"):
    color = px['style'].split("background:")[1].strip()
    x, y = int(px['data-x']), int(px['data-y'])
    if color not in color_groups: color_groups[color] = []
    color_groups[color].append((x, y))

# Generazione SVG finale
scale = 6
svg_width, svg_height = 120 * scale, 80 * scale
svg_content = f'<svg viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">'
svg_content += '\n<style>.obj { transition: 0.3s; cursor: pointer; stroke: rgba(0,0,0,0.1); } .active { fill: #00FF00 !important; filter: drop-shadow(0 0 8px #00FF00); stroke: #000; }</style>'

for color, coords in color_groups.items():
    # Applichiamo il merging
    rectangles = merge_pixels_to_rects(coords)
    
    # ID pulito per il colore
    safe_id = re.sub(r'[^a-zA-Z0-9]', '_', color)
    svg_content += f'\n  <g id="group_{safe_id}" fill="{color}">'
    
    for (rx, ry, rw, rh) in rectangles:
        svg_content += f'\n    <rect x="{rx*scale}" y="{ry*scale}" width="{rw*scale}" height="{rh*scale}" class="obj" />'
    
    svg_content += '\n  </g>'

svg_content += '\n</svg>'

with open("diagramma_merged.svg", "w") as f:
    f.write(svg_content)

print(f"Successo! Creato diagramma_merged.svg con algoritmo di ottimizzazione.")