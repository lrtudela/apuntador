# INT. DÍA

Editor web de guiones para cine y teatro, inspirado en Fade In. Se abre en el navegador, sin cuentas ni instalación, y tus textos no salen de tu equipo.

**Pruébalo: [lrtudela.github.io/int-dia](https://lrtudela.github.io/int-dia)**

<!-- Captura pendiente: añadir cuando estén las notas al margen -->

## Qué hace

- **Cine y teatro.** Cada línea tiene un tipo (acción, personaje, diálogo, paréntesis, escena, transición; en teatro, acotación y acto). `Tab` cambia el tipo y `Enter` pasa a la línea que toca, así que se escribe sin quitar las manos del teclado.
- **Personajes.** Se deducen del texto. Al escribir un nombre se propone el más cercano en gris y se acepta con la flecha derecha. Se pueden renombrar en todo el guion, eligiendo qué menciones cambian.
- **Lugares escritos por el autor.** Las cabeceras de escena no tienen un formato fijo («INT. DÍA», «INT/DÍA»…), así que el programa no las interpreta: das de alta tus lugares y los asignas como etiqueta, para seguirlos por el guion.
- **Deshacer y rehacer propios**, hasta 300 pasos, también en guiones de miles de líneas.
- **Autoguardado** en el navegador, con aviso si falla y si otra pestaña cambia el guion.
- **Portada e impresión a PDF** con numeración de páginas.
- **Papel del actor.** Imprime solo las intervenciones de un personaje, cada una con su pie (la última línea de quien habla antes), y si quieres las acotaciones pegadas a ellas. Pensado para ensayar y legible en blanco y negro.
- **Archivos:** guarda y abre `.intdia.json`, y exporta e importa Fountain para llevar el guion a otros programas.
- **Siete temas** (verde terminal, papel, ámbar, sepia nocturna, azul noche, verde salvia y vaporwave) y funciona en el móvil.
- **Accesible desde el teclado:** `Esc` y luego `Tab` saca el foco del editor.

La ayuda (?) de la propia aplicación lista todos los atajos.

## Cómo está hecho

Un único `index.html` con HTML, CSS y JavaScript puros. Sin dependencias, sin build, sin framework: se puede abrir el archivo directamente. El texto vive en el propio DOM (`contenteditable`, un `div` por línea) y no hay un modelo de datos paralelo. Se publica con GitHub Pages desde `main`.

Las pruebas usan Playwright con Chromium:

```
pip install playwright
playwright install chromium
python tests/test_int_dia.py
```

Se han probado en Chromium y en un móvil real. Safari y Firefox no se han comprobado.

## Licencia

[MIT](LICENSE). Luis Rodríguez Tudela.

---

# INT. DÍA (English summary)

A web editor for screenplays and stage plays, inspired by Fade In. It runs in the browser with no account and no install, and your text never leaves your machine.

**Try it: [lrtudela.github.io/int-dia](https://lrtudela.github.io/int-dia)** (the interface is in Spanish).

It handles film and theatre modes with keyboard-driven line types, character autocomplete and project-wide renaming, author-defined locations used as tags, a custom undo history of 300 steps, autosave, a title page, print to PDF with page numbers, and import/export of Fountain and its own JSON format. It is a single `index.html` with plain HTML, CSS and JavaScript: no dependencies, no build step. Tests run with Playwright (`python tests/test_int_dia.py`).

Released under the [MIT license](LICENSE).
