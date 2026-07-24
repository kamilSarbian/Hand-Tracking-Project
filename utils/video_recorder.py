import queue
import shutil
import subprocess
import threading
import wave
from pathlib import Path

import cv2
import numpy as np

from utils.file_utils import ensure_dir, generate_timestamp_filename

try:
    import imageio_ffmpeg
except Exception:  # pragma: no cover - optional runtime dependency
    imageio_ffmpeg = None

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - optional runtime dependency
    sd = None


class VideoRecorder:
    """
    Writes rendered app frames to a video file.
    """

    def __init__(self, output_dir: str, fps: float = 20.0):
        self.output_dir = ensure_dir(output_dir)
        self.fps = fps
        self.writer = None
        self.is_recording = False
        self.current_file_path = None
        self.temp_video_path = None
        self.current_audio_path = None
        self.audio_sample_rate = 44100
        self.audio_channels = 1
        self.audio_stream = None
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        self.audio_stop_event = threading.Event()
        self.audio_enabled = sd is not None

    def start(self, frame_width: int, frame_height: int):
        if self.is_recording:
            return None

        final_filename = generate_timestamp_filename("recording", "mp4")
        self.current_file_path = str(Path(self.output_dir) / final_filename)
        temp_video_filename = (
            Path(final_filename).with_stem(Path(final_filename).stem + "_video").name
        )
        self.temp_video_path = str(Path(self.output_dir) / temp_video_filename)
        audio_filename = Path(final_filename).with_suffix(".wav").name
        self.current_audio_path = str(Path(self.output_dir) / audio_filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(
            self.temp_video_path, fourcc, self.fps, (frame_width, frame_height)
        )

        if self.writer is None or not self.writer.isOpened():
            if self.writer is not None:
                self.writer.release()
            self.writer = None
            self.is_recording = False
            self.current_file_path = None
            self.temp_video_path = None
            self.current_audio_path = None
            return None

        self._start_audio_recording()
        self.is_recording = True
        return self.current_file_path

    def write(self, frame):
        if self.is_recording and self.writer is not None:
            self.writer.write(frame)

    def stop(self):
        if not self.is_recording:
            return None

        if self.writer is not None:
            self.writer.release()
            self.writer = None

        self._stop_audio_recording()

        self.is_recording = False
        self._finalize_recording_file()
        finished_file = self.current_file_path
        self.current_file_path = None
        self.temp_video_path = None
        self.current_audio_path = None
        return finished_file

    def release(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None

        self._stop_audio_recording()

        self.is_recording = False
        self.current_file_path = None
        self.temp_video_path = None
        self.current_audio_path = None

    def _start_audio_recording(self):
        if not self.audio_enabled or self.current_audio_path is None:
            return

        self.audio_stop_event.clear()
        self.audio_queue = queue.Queue()

        def callback(indata, frames, time_info, status):
            if status:
                return
            self.audio_queue.put(indata.copy())

        def writer_worker():
            with wave.open(self.current_audio_path, "wb") as wav_file:
                wav_file.setnchannels(self.audio_channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.audio_sample_rate)

                while (
                    not self.audio_stop_event.is_set() or not self.audio_queue.empty()
                ):
                    try:
                        chunk = self.audio_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    pcm = np.clip(chunk, -1.0, 1.0)
                    pcm = (pcm * 32767).astype(np.int16)
                    wav_file.writeframes(pcm.tobytes())

        try:
            self.audio_stream = sd.InputStream(
                samplerate=self.audio_sample_rate,
                channels=self.audio_channels,
                dtype="float32",
                callback=callback,
            )
            self.audio_stream.start()
            self.audio_thread = threading.Thread(target=writer_worker, daemon=True)
            self.audio_thread.start()
        except Exception:
            self.audio_stream = None
            self.audio_thread = None

    def _stop_audio_recording(self):
        self.audio_stop_event.set()

        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
            except Exception:
                pass
            self.audio_stream = None

        if self.audio_thread is not None:
            self.audio_thread.join(timeout=2.0)
            self.audio_thread = None

    def _finalize_recording_file(self):
        if self.current_file_path is None or self.temp_video_path is None:
            return

        temp_video = Path(self.temp_video_path)
        final_video = Path(self.current_file_path)
        audio_file = Path(self.current_audio_path) if self.current_audio_path else None

        if not temp_video.exists():
            return

        merged = False
        if (
            audio_file is not None
            and audio_file.exists()
            and audio_file.stat().st_size > 44
        ):
            merged = self._mux_audio_video(temp_video, audio_file, final_video)

        if not merged:
            shutil.move(str(temp_video), str(final_video))
            return

        try:
            temp_video.unlink(missing_ok=True)
            audio_file.unlink(missing_ok=True)
        except Exception:
            pass

    def _mux_audio_video(
        self, video_path: Path, audio_path: Path, output_path: Path
    ) -> bool:
        if imageio_ffmpeg is None:
            return False

        try:
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg_exe,
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(output_path),
            ]
            result = subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.returncode == 0 and output_path.exists()
        except Exception:
            return False
