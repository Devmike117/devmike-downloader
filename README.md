# devmike-downloader - Descargador de Videos y Audios

## Descripción

**Devmike App** es una aplicación de escritorio con interfaz gráfica (Tkinter) que permite descargar videos y audios de múltiples plataformas populares, incluyendo:

- YouTube
- Facebook (videos públicos)
- X (Twitter)
- TikTok
- Instagram (reels, posts)
- Twitch (VODs, clips)
- SoundCloud

La app utiliza `yt-dlp` y `ffmpeg` para realizar las descargas y conversiones, ofreciendo una experiencia sencilla y moderna.

---

## Características

- Interfaz gráfica amigable y moderna.
- Descarga videos y audios de múltiples sitios.
- Soporte para selección de formato (mp3, mp4, etc.).
- Instalación automática de dependencias (`yt-dlp` y `ffmpeg`) si no están presentes.
- Barra de progreso y notificaciones visuales.
- Selección de carpeta de destino.
- Soporte para descargas de listas de reproducción y miniaturas.
- Compatible con Windows (y parcialmente con otros sistemas).

---

## Instalación

1. Descarga el ejecutable desde la sección de releases.
2. Si tu antivirus o navegador muestra advertencias, es por el uso de un certificado autofirmado. El archivo es seguro si lo descargas desde este repositorio oficial.
3. Ejecuta el programa. Si es la primera vez, la app puede instalar automáticamente `yt-dlp` y te avisará si falta `ffmpeg`.

---

## Construcción

- Lenguaje principal: Python 3
- Interfaz: Tkinter
- Descargas: yt-dlp (instalado automáticamente si falta)
- Conversión de formatos: ffmpeg (debe estar instalado en el sistema)
- Empaquetado: PyInstaller (sin UPX, nombre neutro, firmado digitalmente)

---

## Uso

1. Ingresa la URL del video/audio que deseas descargar.
2. Selecciona el formato y la carpeta de destino.
3. Haz clic en "Descargar".
4. La barra de progreso y los mensajes te indicarán el estado de la descarga.

---

## Notas

- Si necesitas instalar ffmpeg, la app te mostrará un botón para descargarlo.
- El ejecutable está firmado digitalmente, pero con un certificado autofirmado (puede mostrar advertencias).
- Para soporte o reportar problemas, abre un issue en este repositorio.

---

¡Disfruta descargando tu contenido favorito de manera sencilla y segura!
