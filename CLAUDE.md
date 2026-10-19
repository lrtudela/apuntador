# INT. DÍA

Editor web de guiones para cine y teatro, inspirado en Fade In. Proyecto de portfolio de Luis: cualquiera debe poder abrir la web y probarlo sin cuentas ni instalación. Se publica con GitHub Pages desde la rama `main`.

## Stack y estructura

- Un único `index.html` con HTML, CSS y JS puros. Sin dependencias, sin build, sin framework. No añadas ninguna sin preguntar.
- `tests/test_int_dia.py`: pruebas con Playwright en Chromium.
- `docs/`: vault de Obsidian con los problemas conocidos, las mejoras y las decisiones pendientes (ver el final de este archivo). Es privado y está en `.gitignore`.
- Interfaz en español; código (variables, funciones) en inglés.

## Cómo funciona (decisiones que no hay que deshacer)

- El DOM es la fuente de verdad: `#ed` contiene un `div` por línea con `data-type`. `lines()` lo lee; no hay un modelo de datos paralelo.
- Los personajes se deducen del texto (líneas `character`), no hay registro aparte. Renombrar reescribe esas líneas. Si el nombre nuevo ya existe, se fusionan. Las menciones en acción, acotación, paréntesis y diálogo solo cambian si el autor las marca en la vista previa (`#ment`).
- Los lugares NO se deducen del texto (las cabeceras no tienen formato fijo), en ningún modo: son una lista del autor (`PL`, `[{id,n}]`) y cada cabecera puede llevar una etiqueta en `data-place` con el id. Se asignan desde el panel Lugares con el cursor en la cabecera; el texto de la cabecera nunca se toca ni se interpreta. Renombrar cambia solo el nombre en la lista (si ya existe, se fusionan); borrar deja sus escenas sin etiqueta. La lista viaja como `p` en el autoguardado, el JSON y el historial; en `l`, las cabeceras etiquetadas llevan un tercer valor con el id. En Fountain, la etiqueta va como nota `[[lugar: Nombre]]` al final de la cabecera.
- Tipos de línea. Cine: action, character, dialogue, paren, heading, transition. Teatro: stage, character, dialogue, paren, heading, act. Tab rota por `CYC[modo]`; Enter usa `NEXT[modo]`. El primer Tab en la línea vacía que Enter acaba de crear salta a `ALT[modo]` (paréntesis tras personaje; acción o acotación tras diálogo) y después sigue el ciclo normal.
- Las líneas `paren` guardan los paréntesis dentro del texto; se quitan al exportar y al cambiar de tipo.
- Deshacer y rehacer son propios (snapshots en `hist`), no los nativos del navegador, porque los cambios de tipo y los renombrados rompen la pila nativa.
- Formato de archivo: Fountain como puente con otros programas (en teatro, actos con `#` y `Mode: teatro` en la portada) y JSON propio. No se leen `.fadein` ni `.fdx`.
- Portada (Archivo › Portada): sus datos viven en el formulario `#cover` (`getCover`/`setCover`), igual que el título vive en `#title`. Viajan en el autoguardado, el JSON (`c`), el historial y la portada Fountain (`Title`, `Credit`, `Author`, `Source`, `Revision`, `Draft date`, `Contact`, `Copyright`, `Notes`; valores de varias líneas sangrados). Email y teléfono van juntos en `Contact`, uno por línea; al leer un `Contact` (o el campo `contact` antiguo) se reparten con `contactParts` y el resto de líneas se descarta. La versión se imprime como «Versión N». Título y crédito vacíos usan el título del proyecto y «escrito por». Solo se imprime si está marcada «Imprimir portada».
- Autoguardado en `localStorage` con la clave `guion:v1`. No la cambies: se perderían los textos guardados en los navegadores.

## Cómo trabajar aquí

- Piensa antes de programar. Si dudas, pregunta; si hay dos caminos, enséñalos antes de elegir.
- Mínimo código que resuelva el problema. Sin funciones, configuración ni abstracciones que no se hayan pedido. Si ves una mejora, propónla en una línea y espera.
- Cambios quirúrgicos: toca solo lo necesario y no reformatees ni reorganices lo que funciona.
- Define el criterio de éxito antes de empezar y no des nada por terminado hasta comprobarlo.
- Estética retro (terminal verde sobre negro, tema papel), móvil primero. El efecto retro nunca debe estorbar a la legibilidad ni a la usabilidad.

## Pruebas

```
pip install playwright
playwright install chromium
python tests/test_int_dia.py
```

Deben pasar todas y no haber errores de JS. Cubren: rotación de tipos con Tab, Enter por modo, autocompletado, renombrar personajes, lugares como etiquetas (alta, recuentos, renombrar, borrar, saltos), ida y vuelta Fountain en cine y teatro, deshacer y rehacer, y 360 px sin scroll horizontal. Las pruebas llaman a funciones globales de `index.html` (`lines`, `rows`, `analyze`, `toFountain`, `parseFountain`, `unparen`, `load`, `PL`) y a los elementos `ED` y `SUG`. Si renombras alguno, actualiza también las pruebas.

## Pendiente y problemas conocidos

Viven en `docs/`, que Luis abre como vault de Obsidian. Antes de trabajar lee `docs/00 Indice.md`. Cada problema, mejora y decisión es una nota con las propiedades `tipo`, `prioridad`, `estado` y `coste`, y con un criterio de éxito comprobable. Al terminar algo, cambia `estado` a `hecho` en su nota; si es un problema, muévela a `docs/problemas/resueltos/` y pasa su enlace a «Resuelto (historial)» en el índice. No la borres. Si creas una nota, enlázala en el índice. No añadas pendientes a este archivo y no edites `docs/Tablero.canvas` ni `docs/.obsidian/`.

`docs/` no se publica: está en `.gitignore`. No lo añadas a ningún commit ni lo saques del `.gitignore`. Al subir cambios, añade solo los archivos que corresponden (`index.html`, `CLAUDE.md`, `tests/`).
