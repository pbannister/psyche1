import argparse
import sys

from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow


def main() -> None:
    """Run the Psyche1 desktop application.

    Optionally accept a directory of known faces so the application can
    perform face recognition alongside detection.
    """
    parser = argparse.ArgumentParser(description="Psyche1 desktop application")
    parser.add_argument(
        "--known-faces-dir",
        help="Directory containing per-person subfolders of known face images.",
        default=None,
    )
    args = parser.parse_args()

    app = QApplication(sys.argv[:1])
    window = MainWindow(known_faces_dir=args.known_faces_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
