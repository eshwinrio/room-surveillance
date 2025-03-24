import cv2
from datetime import datetime
from os import path, getenv, makedirs
from dotenv import load_dotenv
from time import sleep, time
from scp import SCPClient
from async_upload import async_upload, check_remote_directory
from ssh_connection import getSSHConnection

load_dotenv()

# Configuration
HEADLESS_MODE = getenv("HEADLESS_MODE", "False").lower() == "true"
LOCAL_RECORDINGS_DIR = path.expanduser(getenv("LOCAL_WRITE_DIR", "~/recordings"))
MOTION_THRESHOLD = 7000  # Sensitivity for motion detection (lower = more sensitive)
VIDEO_CODEC = "mp4v"  # Video codec for saving files
FRAME_RATE = 20  # Frames per second
UPDATE_FRAME_INTERVAL = 100  # Update first_frame every 100 frames
MOTION_PERSISTENCE = 5  # Number of consecutive frames motion must be detected before recording
COOLDOWN_TIME = 2  # Minimum seconds before stopping recording after motion disappears

ssh = getSSHConnection()

scpClient: SCPClient = SCPClient(ssh.get_transport()) if ssh else None
if scpClient:
    print("[INFO] SCP client initialized.")
else:
    print("[WARNING] SCP client not initialized. Remote upload will be disabled.")

enable_remote_upload = check_remote_directory(ssh) if ssh else False
if enable_remote_upload:
    print("[INFO] Remote directory check passed.")
else:
    print("[WARNING] Remote upload will be disabled.")

if not path.exists(LOCAL_RECORDINGS_DIR):
    makedirs(LOCAL_RECORDINGS_DIR)

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize motion detector
motion_detector = cv2.createBackgroundSubtractorMOG2()

recording = False
video_writer = None
frame_counter = 0
motion_frame_count = 0  # Track consecutive motion frames
last_motion_time = 0  # Track last detected motion time

# Warm-up period to let background subtraction stabilize
print("[INFO] Warming up motion detector...")
for _ in range(30):
    ret, frame = cap.read()
    if not ret:
        break
    motion_detector.apply(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
sleep(2)
print("[INFO] Motion detector ready.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply motion detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    motion_mask = motion_detector.apply(gray)

    # Find contours of motion
    contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    motion_detected = any(cv2.contourArea(c) > MOTION_THRESHOLD for c in contours)

    if motion_detected:
        motion_frame_count += 1
        last_motion_time = time()
    else:
        motion_frame_count = 0 if time() - last_motion_time > COOLDOWN_TIME else motion_frame_count

    if motion_frame_count >= MOTION_PERSISTENCE:
        if not recording:
            # Start recording
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            video_filename = path.join(LOCAL_RECORDINGS_DIR, f"motion_{timestamp}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
            video_writer = cv2.VideoWriter(video_filename, fourcc, FRAME_RATE, (frame.shape[1], frame.shape[0]))
            recording = True
            print(f"[INFO] Motion detected! Recording started: {video_filename}")
        video_writer.write(frame)
    elif recording and time.time() - last_motion_time > COOLDOWN_TIME:
        # Stop recording and upload
        video_writer.release()
        recording = False
        print("[INFO] No motion detected. Recording stopped.")
        
        # Upload only after recording is done
        if scpClient is not None:
            async_upload(scpClient, video_filename)
    
    # Update reference frame periodically
    if frame_counter % UPDATE_FRAME_INTERVAL == 0:
        motion_detector = cv2.createBackgroundSubtractorMOG2()
    
    frame_counter += 1

    # Display (optional, remove if running headless)\
    if not HEADLESS_MODE:
        cv2.putText(frame, "Recording..." if recording else "Idle", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if recording else (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Motion Frames: {motion_frame_count}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("Motion Detection", frame)
        cv2.imshow("Motion Mask", motion_mask)

        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cap.release()
if recording:
    video_writer.release()
cv2.destroyAllWindows()
print("[INFO] Program exited.")
