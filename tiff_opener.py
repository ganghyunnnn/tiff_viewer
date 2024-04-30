import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QShortcut, QLabel
from PyQt5.QtGui import QPixmap, QImage, QFont, QFontMetrics, QColor
from PyQt5.QtCore import Qt, QRect
import cv2
import numpy as np

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TIFF Viewer")
        self.setGeometry(100, 100, 640, 640)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.metadata_label = QLabel(self)
        self.metadata_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.metadata_label.setStyleSheet("background-color: white; border: 1px solid black; padding: 10px;")
        self.metadata_label.hide()
        self.layout.addWidget(self.metadata_label)

        self.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)

        # 드래그 앤 드롭 이벤트 핸들러 설정
        self.setAcceptDrops(True)

        # 이미지 정보 표시 여부 설정
        self.show_image_info = False

        # 이미지 정보 표시 단축키 설정
        self.info_shortcut = QShortcut(Qt.Key_F1, self)
        self.info_shortcut.activated.connect(self.toggle_image_info)

        # Open TIFF 버튼 생성
        self.open_tiff_button = QPushButton("Open TIFF", self)
        self.open_tiff_button.clicked.connect(self.open_tiff)
        self.layout.addWidget(self.open_tiff_button)

        # 이미지 메타 데이터 저장 변수
        self.image_metadata = None

    def toggle_image_info(self):
        self.show_image_info = not self.show_image_info
        if self.show_image_info:
            self.display_image_info()
        else:
            self.metadata_label.hide()

    def display_image_info(self):
        if self.image_metadata:
            width, height, resolution, channels, band_min_max = self.image_metadata
            info_text = f"Image Size: {width}x{height}\n"
            info_text += f"Number of Channels: {channels}\n"
            info_text += "Band Min/Max:\n"
            for i, (min_val, max_val) in enumerate(band_min_max):
                info_text += f"Channel {i + 1}: {min_val}~{max_val}"
                if i < len(band_min_max) - 1:
                    info_text += "\n"  # 마지막 줄을 제외한 줄에 줄 바꿈 추가
            self.metadata_label.setText(info_text)
            self.metadata_label.adjustSize()
            self.metadata_label.show()

    def open_tiff(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open TIFF File", "", "TIFF Files (*.tif *.tiff)", options=options)
        if filename:
            self.load_image(filename)

    def load_image(self, filename):
        image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)

        # 이미지 메타 데이터 저장
        height, width, channel = image.shape
        band_min_max = [(np.min(image[:, :, i]), np.max(image[:, :, i])) for i in range(channel)]
        resolution = (width, height)
        self.image_metadata = (width, height, resolution, channel, band_min_max)

        if image is None:
            print("Error: Unable to open image file.")
            return

        image = cv2.imread(filename, cv2.IMREAD_COLOR)

        # BGR에서 RGB로 변환
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        for i in range(image.shape[2]):
            image[:, :, i] = cv2.normalize(image[:, :, i], None, 0, 255, cv2.NORM_MINMAX)

        height, width, channel = image.shape
        bytes_per_line = channel * width

        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        self.label.setPixmap(pixmap.scaled(self.label.size(), aspectRatioMode=True))


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif')):
                self.load_image(filename)
                break

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        self.scale_image(1.1)

    def zoom_out(self):
        self.scale_image(0.9)

    def scale_image(self, factor):
        pixmap = self.label.pixmap()
        if pixmap is not None:
            new_width = int(pixmap.width() * factor)
            new_height = int(pixmap.height() * factor)
            pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)
            self.label.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'start_pos'):
            if event.buttons() == Qt.LeftButton:
                delta = event.pos() - self.start_pos
                self.label.move(self.label.x() + delta.x(), self.label.y() + delta.y())
                self.start_pos = event.pos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())
