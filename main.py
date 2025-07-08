import os
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import mediapipe as mp
from pathlib import Path

# Compute absolute output directory next to this script
SCRIPT_PATH = Path(__file__).parent
OUTPUT_DIR = SCRIPT_PATH / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"[INFO] Output directory is: {OUTPUT_DIR.resolve()}")

# Global state
regime = None      # "Detect" or "Blur"
mode = None        # "image", "video", "webcam"
filepath = None
frame_rate = None

# Mediapipe setup
mp_face_detection = mp.solutions.face_detection

def process_frame(frame, face_detection, regime):
    H, W = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb)

    if results.detections:
        for det in results.detections:
            bb = det.location_data.relative_bounding_box
            x1 = int(bb.xmin * W)
            y1 = int(bb.ymin * H)
            w  = int(bb.width * W)
            h  = int(bb.height * H)

            if regime == "Blur":
                roi = frame[y1:y1+h, x1:x1+w]
                frame[y1:y1+h, x1:x1+w] = cv2.blur(roi, (30,30))
            else:  # Detect
                cv2.rectangle(frame, (x1,y1), (x1+w, y1+h), (0,255,0), 2)

    return frame

def run_processing():
    global filepath, frame_rate, regime, mode

    if not (regime and mode):
        messagebox.showwarning("Error", "You must select both regime and mode.")
        return

    with mp_face_detection.FaceDetection(model_selection=0,
                                         min_detection_confidence=0.5) as face_det:

        if mode == "image":
            img = cv2.imread(filepath)
            if img is None:
                messagebox.showerror("Error", f"Could not open {filepath}")
                return

            out = process_frame(img, face_det, regime)
            save_path = OUTPUT_DIR / "output.png"
            cv2.imwrite(str(save_path), out)
            message = f"Saved processed image to:\n{save_path.resolve()}"
            print("[INFO]", message.replace("\n", " "))
            messagebox.showinfo("Done", message)

        elif mode == "video":
            cap = cv2.VideoCapture(filepath)
            if not cap.isOpened():
                messagebox.showerror("Error", f"Could not open {filepath}")
                return

            # read fps
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30  # fallback
            frame_rate = fps
            print(f"[INFO] Video FPS = {frame_rate}")

            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Error", "Cannot read first frame of video.")
                return

            h, w = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'MP4V')
            out_path = OUTPUT_DIR / "output.mp4"
            out_vid = cv2.VideoWriter(str(out_path), fourcc, frame_rate, (w, h))

            while ret:
                proc = process_frame(frame, face_det, regime)
                out_vid.write(proc)
                ret, frame = cap.read()

            cap.release()
            out_vid.release()

            message = f"Saved processed video to:\n{out_path.resolve()}"
            print("[INFO]", message.replace("\n", " "))
            messagebox.showinfo("Done", message)

        elif mode == "webcam":
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot access webcam.")
                return

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                proc = process_frame(frame, face_det, regime)
                cv2.imshow("Webcam", proc)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                if cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE) < 1:
                    break

            cap.release()
            cv2.destroyAllWindows()

def choose_file_and_run(selected_mode):
    global mode, filepath
    mode = selected_mode

    if mode in ("image", "video"):
        filetypes = [
            ("Images", "*.jpg *.jpeg *.png") if mode=="image" else ("Videos", "*.mp4 *.avi *.mov"),
            ("All files", "*.*")
        ]
        sel = filedialog.askopenfilename(title=f"Select {mode} file", filetypes=filetypes)
        if not sel:
            return
        filepath = sel
    run_processing()

def on_regime_choice(choice):
    global regime
    regime = choice
    btn_detect.pack_forget()
    btn_blur.pack_forget()

    # Show mode buttons
    for text, m in [("Image","image"), ("Video","video"), ("Webcam","webcam")]:
        b = tk.Button(root, text=text,
                      width=20,
                      command=lambda mm=m: choose_file_and_run(mm))
        b.pack(pady=5)

# Build GUI
root = tk.Tk()
root.title("Face Detect / Blur")

tk.Label(root, text="Choose regime:", font=("Arial",24)).pack(pady=16)

btn_detect = tk.Button(root, text="Detect",
                       width=48,
                       command=lambda: on_regime_choice("Detect"))
btn_detect.pack(pady=5)

btn_blur = tk.Button(root, text="Blur",
                     width=48,
                     command=lambda: on_regime_choice("Blur"))
btn_blur.pack(pady=10)

root.mainloop()
