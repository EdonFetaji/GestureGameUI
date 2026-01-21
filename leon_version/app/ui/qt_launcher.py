import sys
import webbrowser

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QStackedWidget,
    QDialog,
)

from app.core.background_runner import GestureBackgroundWorker
from app.core.ui_gesture_worker import UIGestureWorker

SUBWAY_URL = "https://poki.com/en/g/subway-surfers"
TEMPLE_URL = "https://poki.com/en/g/temple-run-2"


class GameRunningDialog(QDialog):
    def __init__(self, profile: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Running")
        self.setModal(True)
        self.setMinimumSize(640, 320)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(18)

        title = QLabel("Game is running!")
        title.setStyleSheet("font-size: 28px; font-weight: 950;")
        title.setAlignment(Qt.AlignCenter)

        # ✅ Use HTML + <br> (since QLabel becomes RichText)
        info = QLabel(
            f"""
            Selected: <b>{profile}</b><br><br>
            Gesture control is now running in the background.<br>
            Make sure the browser tab is focused.<br><br>
            You can return to the menu anytime.
            """
        )
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)  # ✅ makes text wrap nicely
        info.setStyleSheet("font-size: 15px; color: #cfcfcf; line-height: 1.4;")

        btn_quit = QPushButton("Return to Menu")
        btn_quit.setFixedWidth(340)
        btn_quit.setMinimumHeight(60)
        btn_quit.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(btn_quit, alignment=Qt.AlignCenter)  # ✅ CENTERED

        self.setStyleSheet("""
            QDialog { background: #0f0f0f; }
            QLabel { color: white; }

            QPushButton {
                background: rgba(32,32,32,0.92);
                color: white;
                border: 1px solid rgba(255,255,255,0.16);
                border-radius: 20px;
                font-size: 18px;
                font-weight: 900;
                padding: 16px;
            }
            QPushButton:hover {
                border: 1px solid rgba(255,255,255,0.28);
                background: rgba(38,38,38,0.94);
            }
            QPushButton:pressed {
                background: #00c853;
                color: #101010;
                border: 2px solid #00ff00;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture Recognition Game ")
        self.setMinimumSize(960, 580)

        # Background gesture control for games
        self.game_worker = None

        # Gesture control for UI navigation (no camera window shown)
        self.ui_worker = UIGestureWorker()
        self.ui_worker.action_signal.connect(self.on_ui_gesture)
        self.ui_worker.start()

        # Disable UI gestures when popup is open
        self.ui_nav_enabled = True

        # Stacked pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.page_menu = self.build_main_menu()
        self.page_play = self.build_play_menu()
        self.page_help = self.build_help_page()

        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_play)
        self.stack.addWidget(self.page_help)

        self.stack.setCurrentWidget(self.page_menu)

        # Hover selection index
        self.hover_index = 0

        # Global Styling
        self.setStyleSheet("""
            QMainWindow { background: #0f0f0f; }
            QLabel { color: white; }

            QPushButton {
                background: rgba(32,32,32,0.92);
                color: white;
                border: 1px solid rgba(255,255,255,0.16);
                border-radius: 20px;
                font-size: 18px;
                font-weight: 800;
                padding: 16px;
            }
            QPushButton:hover {
                border: 1px solid rgba(255,255,255,0.28);
                background: rgba(38,38,38,0.94);
            }
            QPushButton:pressed {
                background: #00c853;   /* ✅ click feedback */
                color: #101010;
                border: 2px solid #00ff00;
            }
        """)

        self.update_hover()

    # ---------------- UI HELPERS ----------------

    def _make_button(self, text: str, width=420):
        b = QPushButton(text)
        b.setFixedWidth(width)
        b.setMinimumHeight(66)
        b.setCursor(Qt.PointingHandCursor)
        b.setFocusPolicy(Qt.NoFocus)
        return b

    def _simulate_press_and_click(self, button: QPushButton):
        """
        ✅ Shows the pressed UI even for gesture "SPACE"
        """
        button.setProperty("gesturePressed", True)
        button.setStyleSheet(button.styleSheet() + """
            QPushButton[gesturePressed="true"] {
                background: #00c853;
                color: #101010;
                border: 2px solid #00ff00;
            }
        """)
        button.style().unpolish(button)
        button.style().polish(button)

        # Release after short time + click
        def release():
            button.setProperty("gesturePressed", False)
            button.style().unpolish(button)
            button.style().polish(button)
            button.click()

        QTimer.singleShot(130, release)

    # ---------------- UI BUILDERS ----------------

    def build_main_menu(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.setSpacing(18)

        title = QLabel("Gesture Recognition Game")
        title.setStyleSheet("font-size: 46px; font-weight: 950;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Use hand gestures to control the menu")
        subtitle.setStyleSheet("font-size: 16px; color: #bdbdbd;")
        subtitle.setAlignment(Qt.AlignCenter)

        self.btn_play = self._make_button("Play Game")
        self.btn_test = self._make_button("Test Functionality")
        self.btn_help = self._make_button("Help")
        self.btn_quit = self._make_button("Quit")

        self.btn_play.clicked.connect(self.goto_play)
        self.btn_test.clicked.connect(self.launch_test_controller)
        self.btn_help.clicked.connect(self.goto_help)
        self.btn_quit.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(28)

        layout.addWidget(self.btn_play, alignment=Qt.AlignCenter)
        layout.addWidget(self.btn_test, alignment=Qt.AlignCenter)
        layout.addWidget(self.btn_help, alignment=Qt.AlignCenter)
        layout.addWidget(self.btn_quit, alignment=Qt.AlignCenter)

        hint = QLabel("Closed Fist (👊) = Move   |   Thumb Up (👍) = Select")
        hint.setStyleSheet("font-size: 13px; color: #a5a5a5; margin-top: 26px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        return page

    def build_play_menu(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.setSpacing(18)

        title = QLabel("Choose a Game")
        title.setStyleSheet("font-size: 40px; font-weight: 950;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Selecting a game opens it and enables gestures automatically")
        subtitle.setStyleSheet("font-size: 15px; color: #bdbdbd;")
        subtitle.setAlignment(Qt.AlignCenter)

        self.btn_subway = self._make_button("🚇  Subway Surfers", width=460)
        self.btn_temple = self._make_button("🏃  Temple Run 2", width=460)
        self.btn_back = self._make_button("Back", width=460)

        self.btn_subway.clicked.connect(lambda: self.start_game("Subway Surfers", SUBWAY_URL))
        self.btn_temple.clicked.connect(lambda: self.start_game("Temple Run", TEMPLE_URL))
        self.btn_back.clicked.connect(self.goto_menu)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)

        layout.addWidget(self.btn_subway, alignment=Qt.AlignCenter)
        layout.addWidget(self.btn_temple, alignment=Qt.AlignCenter)
        layout.addSpacing(8)
        layout.addWidget(self.btn_back, alignment=Qt.AlignCenter)

        return page

    def build_help_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.setSpacing(18)

        title = QLabel("Help")
        title.setStyleSheet("font-size: 42px; font-weight: 950;")
        title.setAlignment(Qt.AlignCenter)

        info = QLabel(
            """
            <b>Launcher controls</b><br>
            
            👊 Closed Fist → Move through buttons<br>
            👍 Thumb Up → Select / Click<br><br>

            <b>Game gestures</b><br>
            
            ✌️ Victory → LEFT<br>
            🤟 ILoveYou → RIGHT<br>
            ☝️ Pointing_Up → JUMP<br>
            ✊ Closed_Fist → DUCK<br>
            👍 Thumb_Up → SPACE<br><br>

            <b>Tips</b><br>
            
            Keep the browser window focused<br>
            Better lighting = better detection<br>
            Stay close enough so your hand is visible
            """
        )

        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)  # ✅ IMPORTANT
        info.setStyleSheet("font-size: 16px; color: #d2d2d2; line-height: 1.4;")

        self.btn_help_back = self._make_button("⬅  Back", width=520)
        self.btn_help_back.clicked.connect(self.goto_menu)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addSpacing(12)
        layout.addWidget(self.btn_help_back, alignment=Qt.AlignCenter)

        return page

    # ---------------- HOVER SYSTEM ----------------

    def current_buttons(self):
        page = self.stack.currentWidget()
        if page == self.page_menu:
            return [self.btn_play, self.btn_test, self.btn_help, self.btn_quit]
        if page == self.page_play:
            return [self.btn_subway, self.btn_temple, self.btn_back]
        if page == self.page_help:
            return [self.btn_help_back]
        return []

    def update_hover(self):
        buttons = self.current_buttons()
        if not buttons:
            return

        self.hover_index %= len(buttons)

        for i, b in enumerate(buttons):
            if i == self.hover_index:
                b.setStyleSheet("""
                    QPushButton {
                        background: rgba(32,32,32,0.92);
                        color: white;
                        border: 2px solid #00ff00;
                        border-radius: 20px;
                        font-size: 18px;
                        font-weight: 900;
                        padding: 16px;
                    }
                    QPushButton:pressed {
                        background: #00c853;
                        color: #101010;
                        border: 2px solid #00ff00;
                    }
                """)
            else:
                b.setStyleSheet("""
                    QPushButton {
                        background: rgba(32,32,32,0.92);
                        color: white;
                        border: 1px solid rgba(255,255,255,0.16);
                        border-radius: 20px;
                        font-size: 18px;
                        font-weight: 800;
                        padding: 16px;
                    }
                    QPushButton:pressed {
                        background: #00c853;
                        color: #101010;
                        border: 2px solid #00ff00;
                    }
                """)

    def hover_next(self):
        self.hover_index += 1
        self.update_hover()

    def click_hovered(self):
        buttons = self.current_buttons()
        if not buttons:
            return
        self._simulate_press_and_click(buttons[self.hover_index])

    # ---------------- GESTURE HANDLING ----------------

    def on_ui_gesture(self, action: str):
        """
        ✅ Closed_Fist -> Move selection
        ✅ Thumb_Up -> Click selection
        """
        if not self.ui_nav_enabled:
            return

        if action == "DUCK":  # Closed_Fist mapped to DUCK
            self.hover_next()

        elif action == "SPACE":  # Thumb_Up mapped to SPACE
            self.click_hovered()

    # ---------------- NAVIGATION ----------------

    def goto_play(self):
        self.stack.setCurrentWidget(self.page_play)
        self.hover_index = 0
        self.update_hover()

    def goto_menu(self):
        self.stack.setCurrentWidget(self.page_menu)
        self.hover_index = 0
        self.update_hover()

    def goto_help(self):
        self.stack.setCurrentWidget(self.page_help)
        self.hover_index = 0
        self.update_hover()

    # ---------------- GAME START ----------------

    def start_game(self, profile, url):
        """
        ✅ Opens game
        ✅ Starts background gesture control
        ✅ Popup disables app gestures while open
        """
        self.stop_game_worker()
        webbrowser.open(url)

        self.game_worker = GestureBackgroundWorker(profile=profile)
        self.game_worker.start()

        # disable launcher gestures while popup is open
        self.ui_nav_enabled = False
        dialog = GameRunningDialog(profile, self)
        dialog.exec()
        self.ui_nav_enabled = True

        self.goto_menu()

    def stop_game_worker(self):
        if self.game_worker and self.game_worker.isRunning():
            self.game_worker.stop()
            self.game_worker.wait()
            self.game_worker = None

    # ---------------- TEST ----------------

    def launch_test_controller(self):
        import subprocess, os

        base_dir = os.path.dirname(os.path.abspath(__file__))
        main_path = os.path.join(base_dir, "../gesture_test.py")

        try:
            subprocess.Popen([sys.executable, main_path], cwd=base_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not run gesture_test.py:\n{e}")

    # ---------------- CLOSE ----------------

    def closeEvent(self, event):
        self.stop_game_worker()

        if self.ui_worker and self.ui_worker.isRunning():
            self.ui_worker.stop()
            self.ui_worker.wait()

        event.accept()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()