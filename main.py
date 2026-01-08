from core.ui import QApplication, MapWindow
import sys

app = QApplication(sys.argv)
window = MapWindow()
window.show()
sys.exit(app.exec_())