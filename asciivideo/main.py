import argparse
import os
import sys
import time
import cv2
import numpy as np
import pygame

# Presets de caracteres ASCII según el estilo deseado
ASCII_PRESETS = {
    "Estándar": " .:-=+*#%@",
    "Detallado": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@@",
    "Bloques (Minimalista)": " ░▒▓█",
    "Binario": " 01",
    "Símbolos": " .:+*#@"
}

def get_ffmpeg_path():
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg")
    if os.path.exists(local_path):
        return local_path
    return "ffmpeg"

def main():
    parser = argparse.ArgumentParser(description="Reproductor de video ascii para la terminal con sonido")
    parser.add_argument("video", help="Ruta al archivo de video")
    parser.add_argument("-w", "--width", type=int, default=120, help="Ancho en caracteres de la terminal")
    parser.add_argument("-s", "--style", type=str, default="Estándar", choices=list(ASCII_PRESETS.keys()), help="Estilo de caracteres ASCII")
    parser.add_argument("--invert", action="store_true", help="Invertir los colores (para fondo claro)")
    parser.add_argument("--mute", action="store_true", help="Silenciar el audio")
    parser.add_argument("--loop", action="store_true", help="Reproducir en bucle")
    args = parser.parse_args()

    video_path = args.video
    if not os.path.exists(video_path):
        print(f"Error: No se encuentra el archivo {video_path}", file=sys.stderr)
        sys.exit(1)

    ascii_chars = ASCII_PRESETS.get(args.style, ASCII_PRESETS["Estándar"])
    if args.invert:
        ascii_chars = ascii_chars[::-1]

    pygame.mixer.init()
    audio_temp = os.path.join(os.getcwd(), "temp_audio.wav")
    
    # Extraer Audio si no está silenciado
    if not args.mute:
        ffmpeg_bin = get_ffmpeg_path()
        ffmpeg_cmd = [
            ffmpeg_bin, "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", audio_temp
        ]
        try:
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # Ocultar cursor de la terminal
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()

    try:
        while True:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Error: No se pudo abrir el video {video_path}", file=sys.stderr)
                break

            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0 or fps != fps:
                fps = 30.0
            frame_delay = 1.0 / fps

            # Iniciar Audio con Pygame
            if not args.mute and os.path.exists(audio_temp):
                try:
                    pygame.mixer.music.load(audio_temp)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"Error reproduciendo audio: {e}", file=sys.stderr)

            os.system('cls' if os.name == 'nt' else 'clear')

            start_time = time.time()
            frame_count = 0
            num_chars = len(ascii_chars)

            try:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    h, w = frame.shape[:2]
                    new_h = int(args.width * (h / w) * 0.55)
                    resized = cv2.resize(frame, (args.width, new_h))
                    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

                    ascii_str = ""
                    for row in gray:
                        for pixel in row:
                            ascii_str += ascii_chars[int(pixel / 256 * num_chars)]
                        ascii_str += "\n"

                    sys.stdout.write("\033[H" + ascii_str)
                    sys.stdout.flush()

                    frame_count += 1
                    target_time = start_time + (frame_count * frame_delay)
                    sleep_time = target_time - time.time()
                    if sleep_time > 0:
                        time.sleep(sleep_time)

            except KeyboardInterrupt:
                args.loop = False
            finally:
                cap.release()
                pygame.mixer.music.stop()

            if not args.loop:
                break

    finally:
        # Restaurar cursor y limpiar temporales
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()
        pygame.mixer.quit()
        if os.path.exists(audio_temp):
            try:
                os.remove(audio_temp)
            except Exception:
                pass
        print("\nReproducción finalizada.")

if __name__ == "__main__":
    main()