"""Pruebas de Apuntador. Uso: python tests/test_apuntador.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import sys

URL = (Path(__file__).resolve().parent.parent / "index.html").as_uri()
errs, fails = [], []

def check(name, cond, extra=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{extra}]" if (extra and not cond) else ""))
    if not cond: fails.append(name)

def types(p): return p.evaluate("[...ED.children].map(d=>d.dataset.type)")
def texts(p): return p.evaluate("[...ED.children].map(d=>d.textContent)")

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1100, "height": 800})
    p = ctx.new_page()
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    p.on("dialog", lambda d: d.accept())
    p.goto(URL)

    # 0. demo loaded
    check("demo carga 7 líneas", len(types(p)) == 7, types(p))
    check("panel personajes ANA y LUIS", set(p.evaluate("[...analyze().chars.keys()]")) == {"ANA", "LUIS"})

    # 1. Enter / Tab
    p.click("#ed > div:last-child"); p.keyboard.press("End")
    p.keyboard.press("Enter")
    check("Enter tras diálogo (cine) -> personaje", types(p)[-1] == "character", types(p))
    p.keyboard.press("Tab")
    check("Tab en línea nueva tras diálogo -> acción", types(p)[-1] == "action", types(p))
    p.keyboard.press("Tab")
    check("Tab acción -> personaje", types(p)[-1] == "character")
    p.keyboard.press("Shift+Tab")
    check("Shift+Tab personaje -> acción", types(p)[-1] == "action")
    p.keyboard.press("Tab")
    p.keyboard.type("an")
    p.wait_for_timeout(100)
    sug = p.evaluate("[...SUG.children].map(b=>b.textContent)")
    check("sugerencia ANA al escribir 'an'", sug == ["ANA"], sug)
    p.keyboard.press("Control+Space")
    check("Ctrl+Espacio completa ANA", texts(p)[-1] == "ANA", texts(p))
    p.keyboard.press("Enter")
    check("Enter tras personaje -> diálogo", types(p)[-1] == "dialogue")
    p.keyboard.press("Tab")
    check("Tab en línea nueva tras personaje -> paréntesis", types(p)[-1] == "paren", types(p))
    p.keyboard.press("Shift+Tab")
    p.keyboard.type("Hola")
    p.keyboard.press("Enter"); p.keyboard.press("Tab"); p.keyboard.press("Tab")
    check("el segundo Tab sigue el ciclo normal", types(p)[-1] == "character", types(p))
    p.keyboard.press("Backspace")
    check("vuelta a la línea Hola", texts(p)[-1] == "Hola", texts(p))
    p.keyboard.press("Tab"); p.keyboard.press("Tab")  # dialogue -> paren -> heading? check order
    check("Tab x2 desde diálogo -> escena", types(p)[-1] == "heading", types(p))
    p.keyboard.press("Shift+Tab")
    check("Shift+Tab -> paréntesis con ()", types(p)[-1] == "paren" and texts(p)[-1].startswith("(") and texts(p)[-1].endswith(")"), texts(p)[-1])
    p.keyboard.press("Shift+Tab")  # back to dialogue; parens removed
    check("al salir de paréntesis se quitan", texts(p)[-1] == "Hola", texts(p)[-1])

    # Shift+Enter keeps type
    p.keyboard.press("Shift+Enter")
    check("Mayús+Enter mantiene tipo", types(p)[-1] == "dialogue" and types(p)[-2] == "dialogue")
    p.keyboard.press("Backspace")  # empty line remove
    p.wait_for_timeout(500)

    # 2. rename personaje
    p.click('#panel nav button[data-t=per]')
    items = p.evaluate("[...document.querySelectorAll('#lPer li')].map(l=>l.dataset.k)")
    check("lista personajes", "ANA" in items and "LUIS" in items, items)
    p.click("#lPer li[data-k=ANA] button[data-r]")
    p.keyboard.press("Control+A"); p.keyboard.type("María"); p.keyboard.press("Enter")
    ch = p.evaluate("lines().filter(l=>l.type=='character').map(l=>l.text)")
    check("renombrar ANA -> MARÍA en todas las llamadas", "ANA" not in ch and ch.count("MARÍA") == 2, ch)
    # fusionar
    # rename lugar
    p.click('#panel nav button[data-t=lug]')
    p.click("#lLug li[data-k=COCINA] button[data-r]")
    p.keyboard.press("Control+A"); p.keyboard.type("Salón"); p.keyboard.press("Enter")
    hd = p.evaluate("lines().filter(l=>l.type=='heading').map(l=>l.text)")
    check("renombrar lugar conserva INT. y hora", hd[0] == "INT. SALÓN - NOCHE", hd)

    # 3. roundtrip fountain
    ok = p.evaluate("""()=>{const a=lines().map(l=>[l.type,l.type==='paren'?unparen(l.text):l.text]);
      const f=toFountain();const d=parseFountain(f);return JSON.stringify(a)===JSON.stringify(d.l)||JSON.stringify([a,d.l,f])}""")
    check("Fountain ida y vuelta (cine)", ok is True, ok)

    # 4. undo
    p.click("#ed > div:first-child")
    p.keyboard.press("Control+z")
    ch = p.evaluate("lines().filter(l=>l.type=='character').map(l=>l.text)")
    check("deshacer renombrado de lugar", p.evaluate("lines()[0].text") == "INT. COCINA - NOCHE", p.evaluate("lines()[0].text"))
    p.keyboard.press("Control+z")
    ch = p.evaluate("lines().filter(l=>l.type=='character').map(l=>l.text)")
    check("deshacer renombrado de personaje", "ANA" in ch and "MARÍA" not in ch, ch)
    p.keyboard.press("Control+y")
    ch = p.evaluate("lines().filter(l=>l.type=='character').map(l=>l.text)")
    check("rehacer", "MARÍA" in ch, ch)

    # 5. teatro
    p.select_option("#mode", "teatro")
    ty = types(p)
    check("cine->teatro convierte acción en acotación", "action" not in ty and "stage" in ty, ty)
    p.click("#ed > div:last-child"); p.keyboard.press("End")
    p.keyboard.press("Enter")
    check("Enter tras diálogo (teatro) -> personaje", types(p)[-1] == "character", types(p))
    p.keyboard.press("Tab")
    check("Tab en línea nueva tras diálogo (teatro) -> acotación", types(p)[-1] == "stage", types(p))
    p.keyboard.press("Shift+Tab")  # acotación -> acto (vuelta al final del ciclo)
    p.wait_for_timeout(50)
    check("ciclo teatro llega a acto", types(p)[-1] == "act", types(p)[-1])
    p.keyboard.type("Acto primero")
    p.keyboard.press("Enter")
    check("Enter tras acto -> escena", types(p)[-1] == "heading")
    p.keyboard.type("Plaza"); p.keyboard.press("Enter")
    check("Enter tras escena -> acotación", types(p)[-1] == "stage")
    ok = p.evaluate("""()=>{const N=l=>l.map(([t,x])=>[t,['heading','character'].includes(t)?x.toUpperCase():x]);
      const a=N(lines().filter(l=>l.text.trim()).map(l=>[l.type,l.type==='paren'?unparen(l.text):l.text]));
      const f=toFountain();const d=parseFountain(f);return d.m==='teatro'&&(JSON.stringify(a)===JSON.stringify(N(d.l))||JSON.stringify([a,d.l,f]))}""")
    check("Fountain ida y vuelta (teatro, con actos)", ok is True, ok)
    p.wait_for_timeout(500)
    lug = p.evaluate("[analyze().locs.size, document.querySelector('#panel nav [data-t=lug]').hidden]")
    check("teatro: sin lugares y pestaña Lugares oculta", lug == [0, True], lug)

    # 6. móvil
    m = ctx.new_page(); m.set_viewport_size({"width": 360, "height": 700})
    m.goto(URL)
    sw = m.evaluate("[document.documentElement.scrollWidth, innerWidth, document.getElementById('wrap').scrollWidth, document.getElementById('wrap').clientWidth]")
    check("360px sin scroll horizontal", sw[0] <= 360 and sw[2] <= sw[3], sw)
    m.click("#menu summary")
    mr = m.evaluate("(()=>{const r=document.querySelector('#menu>div').getBoundingClientRect();return [r.left,r.right]})()")
    check("menú Archivo cabe en 360px", mr[0] >= 0 and mr[1] <= 360, mr)
    m.click("#menu summary")
    m.click("#bpanel"); m.wait_for_timeout(250)
    m.click('#panel nav button[data-t=per]')
    m.click("#lPer li[data-k=LUIS] span")
    check("saltar a personaje cierra panel", "open" not in (m.get_attribute("#panel", "class") or ""))

    # 7. propuesta de personaje en la línea
    g = b.new_context(viewport={"width": 1100, "height": 800}).new_page()
    g.on("pageerror", lambda e: errs.append(str(e)))
    g.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    g.goto(URL)
    nt = [g.evaluate(f"load('x','{m}',[]),[...ED.children].map(d=>d.dataset.type)") for m in ("cine", "teatro")]
    check("documento nuevo empieza por escena (cine y teatro)", nt == [["heading"], ["heading"]], nt)
    g.evaluate("load('x','cine',[['character','MARÍA'],['dialogue','a'],['character','MARCOS'],['dialogue','b'],['character','']])")
    ghost = lambda: g.evaluate("ED.lastElementChild.dataset.ghost||''")
    g.click("#ed > div:last-child")
    g.keyboard.type("mar")
    check("propone en gris el más cercano que no acaba de hablar", ghost() == "ÍA", ghost())
    g.keyboard.press("Enter")
    check("Enter acepta la propuesta y salta a diálogo", texts(g)[-2] == "MARÍA" and types(g)[-1] == "dialogue", texts(g))
    check("la propuesta no entra en el texto", "ÍA" not in g.evaluate("JSON.stringify(lines())").replace("MARÍA", ""))
    g.keyboard.press("Enter")  # diálogo -> personaje
    g.keyboard.type("m")
    check("con la misma inicial gana el más cercano", ghost() == "ARCOS", ghost())
    g.keyboard.press("Escape")
    check("Esc descarta la propuesta", ghost() == "")
    g.keyboard.type("arx")
    check("sin coincidencia no se propone nada", ghost() == "")
    g.keyboard.press("Enter")
    check("nombre nuevo se queda tal cual", texts(g)[-2] == "marx" and "MARX" in g.evaluate("[...analyze().chars.keys()]"), texts(g))

    # 8. selector de tema
    theme = lambda: g.evaluate("document.documentElement.dataset.theme||''")
    g.click("#menu summary")
    g.select_option("#theme", "ambar")
    check("el selector aplica el tema", theme() == "ambar", theme())
    g.reload()
    check("el tema se recuerda al recargar", theme() == "ambar" and g.input_value("#theme") == "ambar", theme())
    g.evaluate("localStorage.setItem('guion:theme','inventado')"); g.reload()
    check("tema guardado no válido vuelve a verde", theme() == "" and g.input_value("#theme") == "", theme())

    # 9. portada
    import re
    pages = lambda: int(re.search(rb"/Count (\d+)", g.pdf(format="A4")).group(1))
    g.fill("#title", "El último tren")
    g.evaluate("commit()")
    sin = pages()
    g.click("#menu summary"); g.click("[data-act=cover]")
    check("Portada abre el formulario", g.evaluate("CV.open"))
    check("título del proyecto como sugerencia", g.get_attribute("#cover [name=title]", "placeholder") == "El último tren")
    check("casilla marcada al abrir por primera vez", g.is_checked("#cover [name=on]"))
    g.fill("#cover [name=author]", "Luis Tudela")
    g.keyboard.press("Escape"); g.wait_for_timeout(100)  # el evento close es asíncrono
    check("Esc no guarda nada", g.evaluate("getCover().author") == "" and not g.evaluate("getCover().on"))
    g.click("#menu summary"); g.click("[data-act=cover]")
    g.fill("#cover [name=author]", "Luis Tudela")
    g.fill("#cover [name=version]", "2")
    g.fill("#cover [name=date]", "19/10/2026")
    g.fill("#cover [name=email]", "luis@correo.es")
    g.fill("#cover [name=phone]", "+34 600 000 000")
    g.fill("#cover [name=copyright]", "Registro P.I. M-001234/2026")
    g.click("#cover button[value=ok]"); g.wait_for_timeout(100)
    c = g.evaluate("getCover()")
    check("Guardar guarda la portada", c["author"] == "Luis Tudela" and c["on"] and not g.evaluate("CV.open"), c)
    g.click("#ed > div:first-child"); g.keyboard.press("Control+z")
    check("deshacer quita la portada", g.evaluate("getCover().author") == "", g.evaluate("getCover()"))
    g.keyboard.press("Control+y")
    check("rehacer la devuelve", g.evaluate("getCover()") == c, g.evaluate("getCover()"))
    g.reload()
    check("la portada sobrevive al recargar", g.evaluate("getCover()") == c, g.evaluate("getCover()"))
    ok = g.evaluate("""()=>{const f=toFountain(),d=parseFountain(f),c=getCover();
      return d.t==='El último tren'&&Object.keys(c).every(k=>k==='title'||(d.c[k]||(k==='on'?false:''))===c[k])||JSON.stringify([f,d.c,c])}""")
    check("portada en Fountain ida y vuelta (email y teléfono)", ok is True, ok)
    check("Fountain usa las claves estándar", g.evaluate("/^Title: El último tren\\nAuthor: Luis Tudela\\nRevision: 2\\nDraft date: 19\\/10\\/2026\\nContact:\\n    luis@correo.es\\n    \\+34/.test(toFountain())"), g.evaluate("toFountain()"))
    g.emulate_media(media="print"); g.evaluate("dispatchEvent(new Event('beforeprint'))")
    pc = g.inner_text("#pcover")
    check("la portada impresa lleva todos los datos", all(s in pc for s in ["EL ÚLTIMO TREN", "escrito por", "Luis Tudela", "Versión 2", "luis@correo.es", "+34 600 000 000", "M-001234"]) and g.inner_text("#ptitle") == "", pc)
    g.emulate_media(media=None)  # forzar "screen" también afectaría al PDF
    con = pages()
    check("la portada añade una sola página", con == sin + 1, [sin, con])
    old = g.evaluate("setCover({author:'A',contact:'Luis Tudela\\nluis@correo.es\\n+34 600 000 000'});[getCover().email,getCover().phone]")
    check("el contacto antiguo se reparte en email y teléfono", old == ["luis@correo.es", "+34 600 000 000"], old)

    # 10. aviso de guardado
    s = b.new_context(viewport={"width": 1100, "height": 800}).new_page()
    s.on("pageerror", lambda e: errs.append(str(e)))
    s.goto(URL)
    s.click("#ed > div:last-child"); s.keyboard.press("End"); s.keyboard.type("x"); s.wait_for_timeout(1500)
    check("guardado correcto muestra Guardado", s.inner_text("#saved") == "Guardado", s.inner_text("#saved"))
    s.evaluate("Storage.prototype.setItem=()=>{throw new Error('lleno')}; 0")
    s.keyboard.type("y"); s.wait_for_timeout(1500)
    check("guardado fallido avisa", "No se pudo guardar" in s.inner_text("#saved") and s.get_attribute("#saved", "class") == "err", s.inner_text("#saved"))
    b.close()

print("ERRORES JS:", errs)
print("FALLOS:", fails)
sys.exit(1 if fails or errs else 0)
