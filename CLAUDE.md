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
- Notas al margen: lista aparte (`NT`, `[{id,text,from,versions}]`) y cada línea puede llevar `data-note` con el id. Una nota sobrevive a su línea: si la línea desaparece, queda suelta (se deduce, no se guarda) y se ve en el panel Notas para engancharla o borrarla; `from` guarda el principio de su última línea. Al unir dos líneas se queda la nota de la de arriba. Viajan como `n` en el autoguardado y el JSON; en `l`, la línea con nota lleva un cuarto valor con el id (`''` como lugar si no tiene). En el historial cada nota es una cadena que se reutiliza, como las líneas. Nunca se imprimen. `versions` son textos alternativos de su línea, siempre de una sola línea (sin paréntesis en las `paren`); ⇄ intercambia la versión con el texto de la línea, así que nada se pierde. En Fountain van tras la línea como `[[nota: …]]` y `[[version: …]]` (una línea en blanco dentro de la nota sale con dos espacios; `]]` sale como `] ]`); las sueltas van al final, una por párrafo. Al importar, cualquier otro `[[…]]` pasa a ser la nota de su línea, y uno solo en su línea, una nota suelta.
- Un guion nuevo, o uno al que se borra todo, empieza por una cabecera de escena (cine y teatro), y el selector de tipo la muestra. Al cambiar de modo el selector conserva el tipo de la línea actual. En teatro la cabecera es solo «ESCENA 1»; el lugar va como etiqueta.
- Tipos de línea. Cine: action, character, dialogue, paren, heading, transition. Teatro: stage, character, dialogue, paren, heading, act. Tab rota por `CYC[modo]`; Enter usa `NEXT[modo]`. El primer Tab en la línea vacía que Enter acaba de crear salta a `ALT[modo]` (paréntesis tras personaje; acción o acotación tras diálogo) y después sigue el ciclo normal.
- Las líneas `paren` guardan los paréntesis dentro del texto; se quitan al exportar y al cambiar de tipo.
- Deshacer y rehacer son propios (snapshots en `hist`), no los nativos del navegador, porque los cambios de tipo y los renombrados rompen la pila nativa. Cada paso guarda una cadena por línea y reutiliza las que no cambian (con 6000 líneas y 300 pasos son unos 9 MB); no vuelvas a guardar el guion entero en cada paso.
- Tab rota el tipo de línea, pero Esc y luego Tab (o Mayús+Tab) saca el foco del editor, para que no sea una trampa de teclado. Cualquier otra tecla o perder el foco anula la salida.
- Sugerencia de personaje en gris (`data-ghost`): Tab (y ⇥ en el móvil) o la flecha derecha la aceptan sin cambiar el tipo; Mayús+Tab rota el tipo; Enter confirma siempre lo escrito; Esc la descarta y Tab vuelve a rotar.
- Formato de archivo: Fountain como puente con otros programas (en teatro, actos con `#` y `Mode: teatro` en la portada) y JSON propio. No se leen `.fadein` ni `.fdx`.
- Portada (Archivo › Portada): sus datos viven en el formulario `#cover` (`getCover`/`setCover`), igual que el título vive en `#title`. Viajan en el autoguardado, el JSON (`c`), el historial y la portada Fountain (`Title`, `Credit`, `Author`, `Source`, `Revision`, `Draft date`, `Contact`, `Copyright`, `Notes`; valores de varias líneas sangrados). Email y teléfono van juntos en `Contact`, uno por línea; al leer un `Contact` (o el campo `contact` antiguo) se reparten con `contactParts` y el resto de líneas se descarta. La versión se imprime como «Versión N». Título y crédito vacíos usan el título del proyecto y «escrito por». Solo se imprime si está marcada «Imprimir portada».
- Aviso de copia (`#copy`, `copyMark`): la última copia en archivo (Guardar .json o Exportar .fountain) se guarda en `guion:copia` como `{d,h}`: fecha y hash del contenido copiado (`h` vacío si nunca se copió; entonces `d` es el primer cambio). Hay cambios sin copiar si el hash actual es otro; con más de 7 días se resalta. La demo intacta y el guion vacío no avisan.
- Papel del actor (Archivo › Papel del actor, `roleHTML`/`printRole`): para un personaje, sus intervenciones bajo la cabecera de su escena, cada una con su pie (la última línea `dialogue` entera de la intervención anterior; ninguno si la anterior es suya o es la primera de la escena). Una intervención es el personaje con sus líneas de diálogo y paréntesis. Con «Exportar también acotaciones» salen las acotaciones y paréntesis pegados (sin otra intervención ni cabecera de por medio) a la del actor y a la del pie. Se imprime con `data-print=role` en `<html>` (se quita en `afterprint`) y la página con nombre `role`, cuyo `@top-left` «Papel de X» escribe `#roleCss`. En blanco y negro: lo del actor en negrita con barra; el pie, gris oscuro y cursiva; sin fondos.
- Autoguardado en `localStorage` con la clave `guion:v1`. No la cambies: se perderían los textos guardados en los navegadores. Si otra pestaña guarda, esta carga su versión si no tiene cambios pendientes; si los tiene, deja de guardar y pregunta (`#clash`).

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

Deben pasar todas y no haber errores de JS. Cubren: rotación de tipos con Tab, Enter por modo, autocompletado, renombrar personajes, lugares como etiquetas (alta, recuentos, renombrar, borrar, saltos), notas al margen (crear, deshacer, sueltas, unir y partir líneas, margen cerrado, impresión, móvil, versiones e intercambio, Fountain), aviso de copia (con reloj simulado), papel del actor (pies, acotaciones pegadas, impresión y contraste), tabla de presencias (solo cuenta hablar, actos, renombrar, saltos, 360 px, impresión en bloques), ida y vuelta Fountain en cine y teatro, deshacer y rehacer, dos pestañas a la vez, y 360 px sin scroll horizontal. Las pruebas llaman a funciones globales de `index.html` (`lines`, `rows`, `analyze`, `toFountain`, `parseFountain`, `unparen`, `load`, `PL`, `NT`, `commit`, `renderPanels`, `setCover`, `renderNotes`, `printRole`) y a los elementos `ED` y `SUG`. Si renombras alguno, actualiza también las pruebas.

## Pendiente y problemas conocidos

Viven en `docs/`, que Luis abre como vault de Obsidian. Antes de trabajar lee `docs/00 Indice.md`. Cada problema, mejora y decisión es una nota con las propiedades `tipo`, `prioridad`, `estado` y `coste`, y con un criterio de éxito comprobable. Al terminar algo, cambia `estado` a `hecho` en su nota; si es un problema, muévela a `docs/problemas/resueltos/` y pasa su enlace a «Resuelto (historial)» en el índice. No la borres. Si creas una nota, enlázala en el índice. No añadas pendientes a este archivo y no edites `docs/Tablero.canvas` ni `docs/.obsidian/`.

`docs/` no se publica: está en `.gitignore`. No lo añadas a ningún commit ni lo saques del `.gitignore`. Al subir cambios, añade solo los archivos que corresponden (`index.html`, `CLAUDE.md`, `README.md`, `LICENSE`, `tests/`).
