import argparse
import sys
import time
import cv2
import numpy as np

# Paleta de caracteres de mayor a menor densidad
ASCII_CHARS = np.array(
    list("Ñ@#W$9876543210?!abc;:+=-,._ "), dtype="U1"
)


def frame_to_ascii(frame, width):
  """Convierte un fotograma de OpenCV a una cadena de texto ASCII optimizada."""
  h, w = frame.shape[:2]
  # Ajuste de proporción por el alto de las fuentes de la terminal (~0.55)
  aspect_ratio = h / w
  height = int(width * aspect_ratio * 0.55)

  resized = cv2.resize(frame, (width, height))
  gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

  # Mapeo vectorizado con NumPy para máximo rendimiento
  indices = (gray.astype(float) / 255 * (len(ASCII_CHARS) - 1)).astype(int)
  lines = ["".join(row) for row in ASCII_CHARS[indices]]
  return "\n".join(lines)


def main():
  parser = argparse.ArgumentParser(
      description="Reproductor de video ascii para la terminal"
  )
  parser.add_argument("video", help="Ruta al archivo de video")
  parser.add_argument(
      "-w",
      "--width",
      type=int,
      default=90,
      help="Ancho en caracteres de la terminal",
  )

  args = parser.parse_args()

  cap = cv2.VideoCapture(args.video)
  if not cap.isOpened():
    print(f"[Error] No se pudo abrir el archivo de video: {args.video}")
    sys.exit(1)

  fps = cap.get(cv2.CAP_PROP_FPS)
  frame_duration = 1 / fps if fps > 0 else 1 / 30

  # Ocultar cursor y limpiar pantalla
  sys.stdout.write("\x1b[?25l\x1b[2J")
  sys.stdout.flush()

  try:
    while cap.isOpened():
      start_time = time.time()
      ret, frame = cap.read()
      if not ret:
        break

      ascii_art = frame_to_ascii(frame, args.width)

      # Volver al inicio de la terminal e imprimir sin parpadeo
      sys.stdout.write("\x1b[H" + ascii_art)
      sys.stdout.flush()

      # Control de FPS
      elapsed = time.time() - start_time
      if elapsed < frame_duration:
        time.sleep(frame_duration - elapsed)

  except KeyboardInterrupt:
    pass
  finally:
    # Restaurar cursor
    sys.stdout.write("\x1b[?25h\n")
    cap.release()
    print("Reproducción detenida.")


if __name__ == "__main__":
  main()