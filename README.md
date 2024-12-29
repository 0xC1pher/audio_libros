# Proyecto: Generador de Audiolibros y traducirlos en audio  a espanol

Este proyecto convierte archivos PDF en audiolibros en español, permitiendo seleccionar un rango de páginas específico. Utiliza `Edge_TTS` para la conversión de texto a voz y `pdfplumber` para extraer el texto de los PDFs. Los audiolibros generados se guardan en directorios organizados por título.
- Ahora se divide en -chunks- el textos mas pequenos antes de traducir en las que los fragmentos se traducen sin problemas solo hay que esperar que se haga el trabajo porque las APIS de GOOGLE limitan las traducciones entonces la solucion viable que vi fue esa, si gustas mejorarla puedes hacerlo sin problema!
- Ahora se manejan mejor los errores
- Luego de la separacion en fragmentos ya traducidos , los tragmentos se unen creando un soo archivo para crear un solo audio completo!
- Por ahora no hay mas cambios
