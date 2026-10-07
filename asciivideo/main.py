import argparse
import subprocess
import cv2
import numpy as np
import sys
import time

# Rampa de caracteres de oscuro a claro (puedes cambiarla o invertirla si se sigue viendo mal)
# Si se ve muy blanco, prueba invirtiéndola: "@#S%?*+;:,. "
ASCII_CHARS = " .:-=+*#%@"  # Del menos denso (más oscuro en fondo negro) al más denso

def pixels_to_ascii(image):
    pixels = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Opcional: si quieres el efecto negativo (invertir), descomenta la siguiente línea:
    # pixels = cv2.bitwise_not(pixels)
    
    # Mapear cada píxel a un carácter de la rampa de forma directa
    indices = (pixels / 255 * (len(ASCII_CHARS) - 1)).astype(int)
    
    lines = "".join([ASCII_CHARS[pixel] for row in indices for pixel in row])
    
    width = image.shape[1]
    return "\n".join([lines[i:i+width] for i in range(0, len(lines), width)])

def main():
    parser = argparse.ArgumentParser(description="Reproductor de video ascii para la terminal con sonido")
    parser.add_argument("video", help="Ruta al archivo de video")
    parser.add_argument("-w", "--width", type=int, default=100, help="Ancho en caracteres de la terminal")
    args = parser.parse_args()

    video_path = args.video
    
    # Abrir video con OpenCV
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir el video {video_path}", file=sys.stderr)
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps != fps:
        fps = 30.0  # FPS por defecto si no se detecta
    frame_duration = 1.0 / fps

    # Iniciar reproducción de audio en segundo plano usando ffplay (de ffmpeg)
    # -nodisp oculta la ventana gráfica de video de ffplay, -autoexit cierra al terminar
    audio_process = None
    try:
        audio_process = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", video_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("Aviso: 'ffplay' (ffmpeg) no está instalado. El video se reproducirá sin sonido.", file=sys.stderr)
        print("Puedes instalarlo con: sudo pacman -S ffmpeg", file=sys.stderr)

    # Ocultar cursor de la terminal y limpiar pantalla para evitar parpadeos molestos
    sys.stdout.write("\x1b[?25l")
    
    try:
        while cap.isOpened():
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            # Redimensionar y convertir a ASCII
            resized_frame = cv2.resize(frame, (args.width, int(frame.shape[0] * args.width / frame.shape[1])))
            ascii_str = pixels_to_ascii(resized_frame)

            # Volver arriba en la terminal (ANSI escape code) para sobrescribir y evitar parpadeo
            sys.stdout.write("\x1b[H" + ascii_str)
            sys.stdout.flush()

            # Controlar los fotogramas por segundo (FPS)
            elapsed = time.time() - start_time
            if elapsed < frame_duration:
                time.sleep(frame_duration - elapsed)

    except KeyboardInterrupt:
        pass
    finally:
        # Restaurar cursor al salir
        sys.stdout.write("\x1b[?25h")
        cap.release()
        if audio_process:
            audio_process.terminate()
        print("\nReproducción finalizada.")

if __name__ == "__main__":
    main()