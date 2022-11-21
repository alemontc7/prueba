import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QAction, QMainWindow,
                             qApp, QInputDialog)
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtCore import Qt


class View(QMainWindow):
    """Create main GUI and process the events with controller"""

    def __init__(self, controller, model):
        super().__init__()
        self.top_box = None
        self.gamemenu = None
        self.menubar = None
        self.main_widget = None
        self.controller = controller
        self.controller.setView(self)
        self.controller.start_new_game()
        self.model = model
        self.createMainUI()

    def createMainUI(self):
        self.setGeometry(400, 200, 100, 100)
        self.setFixedWidth(32 * self.model.FIELD_WIDTH + 20)
        self.setFixedHeight(32 * self.model.FIELD_HEIGHT + 90)
        self.setWindowTitle("Minesweeper")
        self.setWindowIcon(QIcon("img/flagged.gif"))
        self.create_menubar()
        self.create_top_box()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(self.top_box)
        self.top_box.setAlignment(Qt.AlignCenter)

    def create_menubar(self):
        self.menubar = self.menuBar()
        self.gamemenu = self.menubar.addMenu("&Game")
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+q")
        exit_action.triggered.connect(qApp.exit)
        self.menubar.addAction(exit_action)

        easy_level = QAction("&Easy mode", self)
        easy_level.triggered.connect(
            self.controller.start_new_game_easy)
        self.gamemenu.addAction(easy_level)

    def create_top_box(self):
        self.top_box = TopBox(self.controller, self.model)

    def inputBox(self):
        name, done1 = QInputDialog.getText(
            self, 'Register', 'Enter your name:')
        return name


class TopBox(QVBoxLayout):
    """Class witch display play button and amount of flagged cells"""

    def __init__(self, controller, model):
        super().__init__()
        self.field = None
        self.top_panel = None
        self.controller = controller
        self.model = model
        self.create_top_panel()
        self.create_field()

    def create_top_panel(self):
        self.top_panel = TopPanel(self.controller, self.model)
        self.addLayout(self.top_panel)

    def create_field(self):
        self.field = Field(self.controller, self.model, self.top_panel)
        self.addWidget(self.field)


class TopPanel(QHBoxLayout):
    """Class witch contains start-game button and mines counter."""

    def __init__(self, controller, model):
        super().__init__()
        self.start_btn = None
        self.board = None
        self.controller = controller
        self.model = model
        self.setAlignment(Qt.AlignHCenter)
        self.setSpacing(56)
        self.create_mines_counter()
        self.create_start_button()

    def create_mines_counter(self):
        self.board = MinesBoard(numbers=3)
        self.board.set(self.model.MINES_MAX)
        self.addLayout(self.board)

    def create_start_button(self):
        self.start_btn = StartButton(self.controller)
        self.addWidget(self.start_btn)


class StartButton(QLabel):
    """Start game button"""

    def __init__(self, controller):
        self.controller = controller
        self.smiles = None
        super().__init__()
        self.load_smiles()
        self.set_start()

    def set_start(self):
        self.setPixmap(self.smiles[0])

    def set_lost(self):
        self.setPixmap(self.smiles[1])

    def set_uhoh(self):
        self.setPixmap(self.smiles[2])

    def set_won(self):
        self.setPixmap(self.smiles[3])

    def load_smiles(self):
        # start-game button icons loading.
        self.smiles = []
        for file in ["", "lost", "uhoh", "won"]:
            _asset = QPixmap("img/smiley{}.gif".format(file))
            _asset = _asset.scaled(44, 44)
            self.smiles.append(_asset)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.controller.start_new_game_smile()
            self.set_start()


class Board(QHBoxLayout):
    """Class for converting integers to beautiful scoreboards."""

    def __init__(self, numbers=3):
        super().__init__()
        self.digits = None
        self.numbers = None
        self.load_digits()
        self.init_board(numbers)

    def init_board(self, numbers):
        self.setSpacing(0)
        self.numbers = []
        for number in range(numbers):
            label = QLabel("")
            label.setPixmap(self.digits[0])
            self.numbers.append(label)
            self.addWidget(label)

    def load_digits(self):
        self.digits = []
        for i in range(11):
            _asset = QPixmap("img/digit{}.gif".format(i))
            _asset = _asset.scaled(25, 25, Qt.KeepAspectRatioByExpanding)
            self.digits.append(_asset)

    def set(self, number: int) -> bool:
        minus = False
        if number < 0:
            minus = True
            number = number * (-1)
        if len(str(number)) > len(self.numbers): return False
        k = 0
        for _number in self.numbers[::-1]:
            if k < len(str(number)):
                k += 1
                _number.setPixmap(self.digits[int(str(number)[-k])])
            else:
                _number.setPixmap(self.digits[0])
        if minus:
            self.numbers[0].setPixmap(self.digits[10])


class MinesBoard(Board):
    pass


class Field(QWidget):
    """Class witch display game field."""

    def __init__(self, controller, model, top_panel):
        super().__init__()
        self.painter = None
        self.assets = None
        self.controller = controller
        self.model = model
        self.top_panel = top_panel
        self.SIZE = 32
        self.last_x = -1
        self.last_y = -1
        self.last_clicked = -1
        self.load_assets()
        self.setFixedWidth(self.SIZE * self.model.FIELD_WIDTH)
        self.setFixedHeight(self.SIZE * self.model.FIELD_HEIGHT)

    def load_assets(self):
        # field cells assets loading.
        self.assets = []
        for i in range(9):
            _asset = QPixmap("img/open{}.gif".format(i))
            _asset = _asset.scaled(self.SIZE, self.SIZE, Qt.IgnoreAspectRatio)
            self.assets.append(_asset)

        files = [
            "blank",  # 9
            "flagged",  # 10
            "question",  # 11
            "mine",  # 12
            "mineclicked",  # 13
            "misflagged",  # 14
        ]

        for file in files:
            _asset = QPixmap("img/{}.gif".format(file))  # index 9
            _asset = _asset.scaled(self.SIZE, self.SIZE, Qt.IgnoreAspectRatio)
            self.assets.append(_asset)

    def mousePressEvent(self, event):
        _x = event.pos().x()
        _y = event.pos().y()
        x = int(_x / self.SIZE)
        y = int(_y / self.SIZE)
        if self.test_mouse_coordinates(_x, _y):
            if self.controller.get_status() == "Game":
                self.last_clicked = self.model.field[y][x].int_state
                self.last_x = x
                self.last_y = y
                if self.model.field[y][x].int_state == 9:
                    if event.button() == Qt.LeftButton:
                        self.model.field[y][x].int_state = 0
                        self.top_panel.start_btn.set_uhoh()
                    self.update()

    def mouseReleaseEvent(self, event):
        _x = event.pos().x()
        _y = event.pos().y()
        x = int(_x / self.SIZE)
        y = int(_y / self.SIZE)
        if self.test_mouse_coordinates(_x, _y):
            status = self.controller.get_status()
            if status == "Game":
                if self.last_x == x and self.last_y == y:
                    if event.button() == Qt.LeftButton:
                        self.controller.left_click(x, y)
                    if event.button() == Qt.RightButton:
                        self.controller.right_click(x, y)
                else:
                    self.model.field[self.last_y][self.last_x].int_state = self.last_clicked
                self.top_panel.start_btn.set_start()
            status = self.controller.get_status()
            if status == "Win":
                self.top_panel.start_btn.set_won()
            if status == "Lose":
                self.top_panel.start_btn.set_lost()

        self.update()

    def test_mouse_coordinates(self, x, y):
        # TODO: Write tests for this method.
        return (0 <= x <= self.SIZE * self.model.FIELD_WIDTH and
                0 <= y <= self.SIZE * self.model.FIELD_HEIGHT)

    def paintEvent(self, event):

        self.painter = QPainter(self)
        for y in range(self.model.FIELD_HEIGHT):
            for x in range(self.model.FIELD_WIDTH):
                asset = self.assets[self.model.field[y][x].int_state]
                self.painter.drawPixmap(x * self.SIZE, y * self.SIZE, asset)

        self.painter.end()