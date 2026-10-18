"""Edge-to-edge image, video, and live-frame widgets for the Axentra kit."""
import os
from pathlib import Path

from PyQt5.QtCore import QRectF, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget


class _ImageSurface(QWidget):
    _image_ready = pyqtSignal(QImage)

    def __init__(self, image=None):
        super().__init__()
        self._image = QImage()
        self._image_ready.connect(self._display_image)
        self.setMinimumSize(1, 1)
        self.setStyleSheet("background:#000000; border:none;")
        if image is not None:
            self.set_image(image)

    def set_image(self, image):
        """Display a local image, QImage, or QPixmap edge-to-edge."""
        qimage = self._to_qimage(image)
        if qimage.isNull():
            return False
        self._image_ready.emit(qimage)
        return True

    def clear(self):
        self._image_ready.emit(QImage())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        if self._image.isNull():
            return

        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        source_width = self._image.width()
        source_height = self._image.height()
        target_ratio = self.width() / self.height()
        source_ratio = source_width / source_height
        if source_ratio > target_ratio:
            crop_width = source_height * target_ratio
            source = QRectF((source_width - crop_width) / 2, 0, crop_width, source_height)
        else:
            crop_height = source_width / target_ratio
            source = QRectF(0, (source_height - crop_height) / 2, source_width, crop_height)
        painter.drawImage(QRectF(self.rect()), self._image, source)

    def _display_image(self, image):
        self._image = image
        self.update()

    @staticmethod
    def _to_qimage(value, color_format="BGR"):
        if isinstance(value, QImage):
            return value.copy()
        if isinstance(value, QPixmap):
            return value.toImage().copy()
        if isinstance(value, (str, bytes, os.PathLike)):
            return QImage(os.fsdecode(value))

        shape = getattr(value, "shape", None)
        if shape is None or getattr(value, "ndim", 0) not in (2, 3):
            raise TypeError("Expected an image path, QImage, QPixmap, or uint8 frame array")
        if str(getattr(value, "dtype", "")) != "uint8":
            raise ValueError("Frame arrays must use uint8 pixels")

        height, width = shape[:2]
        if height < 1 or width < 1:
            raise ValueError("Frame dimensions must be greater than zero")

        channels = 1 if len(shape) == 2 else shape[2]
        if channels == 1 and color_format.upper() == "BGR":
            color_format = "GRAY"
        formats = {
            (1, "GRAY"): QImage.Format_Grayscale8,
            (3, "RGB"): QImage.Format_RGB888,
            (3, "BGR"): QImage.Format_BGR888,
            (4, "RGBA"): QImage.Format_RGBA8888,
            (4, "BGRA"): QImage.Format_ARGB32,
        }
        image_format = formats.get((channels, color_format.upper()))
        if image_format is None:
            raise ValueError("Unsupported frame format: %s with %d channels" % (color_format, channels))

        stride = width * channels
        return QImage(value.tobytes(), width, height, stride, image_format).copy()


class ImageViewer(_ImageSurface):
    """Display a code-supplied image without a title, frame, or controls."""


class FrameWidget(_ImageSurface):
    """Display changing live frames; QImage and uint8 array updates are thread-safe."""

    def set_frame(self, frame, color_format="BGR"):
        """Show a QImage, QPixmap, image path, or uint8 RGB/BGR/OpenCV frame array."""
        image = self._to_qimage(frame, color_format=color_format)
        if image.isNull():
            return False
        self._image_ready.emit(image)
        return True


class VideoPlayer(QVideoWidget):
    """Edge-to-edge video surface controlled entirely through its Python API."""

    playback_error = pyqtSignal(str)

    def __init__(self, source=None):
        super().__init__()
        self.setStyleSheet("background:#000000; border:none;")
        self.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
        self._player = QMediaPlayer(self)
        self._player.setVideoOutput(self)
        self._player.setMuted(True)
        self._player.error.connect(self._emit_playback_error)
        self._player.mediaStatusChanged.connect(self._check_video_available)
        self._player.videoAvailableChanged.connect(self._check_video_available)
        self._video_error_reported = False
        if source is not None:
            self.set_source(source)

    def set_source(self, source):
        """Load a local video path or a URL; return False when a local file is missing."""
        if isinstance(source, QUrl):
            url = source
        else:
            text = os.fsdecode(source) if isinstance(source, (bytes, os.PathLike)) else str(source)
            candidate = QUrl(text)
            if candidate.isValid() and candidate.scheme() in ("http", "https", "rtsp", "rtmp"):
                url = candidate
            else:
                path = Path(text).expanduser()
                if not path.is_file():
                    return False
                url = QUrl.fromLocalFile(str(path.resolve()))

        self._player.stop()
        self._video_error_reported = False
        self._player.setMedia(QMediaContent(url))
        self._player.play()
        return True

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def stop(self):
        self._player.stop()

    def set_volume(self, volume):
        self._player.setVolume(max(0, min(100, int(volume))))

    def set_muted(self, muted):
        self._player.setMuted(bool(muted))

    def _check_video_available(self, *_):
        loaded_statuses = (QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia)
        if (not self._video_error_reported
                and self._player.mediaStatus() in loaded_statuses
                and not self._player.isVideoAvailable()):
            self._video_error_reported = True
            self.playback_error.emit(
                "Qt could not decode a video stream. Re-encode the file as H.264 MP4 (yuv420p)."
            )

    def _emit_playback_error(self, *_):
        self.playback_error.emit(self._player.errorString() or "Unable to play video")
