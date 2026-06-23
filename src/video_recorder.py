import cv2
import numpy as np
import mss
import threading

from pathlib import Path
from datetime import datetime

# resolve path relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = BASE_DIR / "videos"

# ensures the directory exists/ create videos directory if it doesn't exist
VIDEO_DIR.mkdir(exist_ok=True)

recording = False
recording_thread = None

def start_recording(driver, filename="signup_flow.mp4"):

    global recording, recording_thread

    # generate a unique filename using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    video_path = VIDEO_DIR / f"signup_flow_{timestamp}.mp4"

    print("Recording started")
    print("Saving to:", video_path)

    recording = True

    def record():

        with mss.mss() as sct:

            
            rect = driver.get_window_rect()

            # captures the primary monitor
            monitor = sct.monitors[1]

            width = monitor["width"]
            height = monitor["height"]

            # create video writer for MP4 format
            writer = cv2.VideoWriter(
                str(video_path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                10,     # frames per second
                (width, height)
            )

            print("Writer opened:", writer.isOpened())

            while recording:
                # grab screenshot of the monitor
                frame = np.array(
                    sct.grab(monitor)
                )

                # convert BGRA (from mss) to BGR (required by OpenCv) 
                frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGRA2BGR
                )

                writer.write(frame)

            # ensure video is finalized properly
            print("Releasing video writer...")
            writer.release()
            print("Video writer released")

    # run recording in a separate thread so tests can continue executing
    recording_thread = threading.Thread(target=record)
    recording_thread.start()


def stop_recording():

    global recording, recording_thread

    print("Stopping recording...")

    # signal recording loop to stop
    recording = False

    # wait for recording thread to finish cleanup
    if recording_thread:
        recording_thread.join()

    print("Recording stopped")

# clear old videos from the video folder everytime the script runs
def clear_old_recording():
    for video in VIDEO_DIR.glob("*.mp4"):
        video.unlink()