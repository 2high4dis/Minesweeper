from PyQt6.QtCore import Qt, QSize, QEvent, QObject, QTimer, QTime
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QFont, QIcon

import sys
import random
import ctypes


class Window(QMainWindow):
    def __init__(self) -> None:
        super(Window, self).__init__()

        # sizing and positioning

        self.width = 350
        self.height = 280
        self.x = int((1920 - self.width) / 2)
        self.y = int((1080 - self.height) / 2)
        self.setFixedSize(self.width, self.height)
        self.setStyleSheet('background-color: lightgrey;'
                           'font: 20px MS Serif')
        self.setWindowTitle('Minesweeper')
        self.setWindowIcon(QtGui.QIcon('./img/icon.png'))
        appicon = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appicon)
        #self.setGeometry(self.x, self.y)

        self.difficulty = None

        self.title = QtWidgets.QLabel(self, text='Minesweeper')
        self.title.setGeometry(0, 25, self.width, 50)
        self.title.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
        self.title.setStyleSheet('font-size: 40px')

        self.difficulty_label = QtWidgets.QLabel(
            self, text='Choose Difficulty:')
        self.difficulty_label.setGeometry(0, 80, self.width, 30)
        self.difficulty_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)

        self.radiobutton_b = QtWidgets.QRadioButton(self, text="Beginner")
        self.radiobutton_b.difficulty = "Beginner"
        self.radiobutton_b.toggled.connect(self.choose_difficulty)
        self.radiobutton_b.setGeometry(120, 110, 150, 30)

        self.radiobutton_i = QtWidgets.QRadioButton(self, text="Intermediate")
        self.radiobutton_i.difficulty = "Intermediate"
        self.radiobutton_i.toggled.connect(self.choose_difficulty)
        self.radiobutton_i.setGeometry(120, 140, 150, 30)

        self.radiobutton_e = QtWidgets.QRadioButton(self, text="Expert")
        self.radiobutton_e.difficulty = "Expert"
        self.radiobutton_e.toggled.connect(self.choose_difficulty)
        self.radiobutton_e.setGeometry(120, 170, 150, 30)

        self.start_button = QtWidgets.QPushButton(self, text='Start game')
        self.start_button.setGeometry(125, 220, 100, 30)
        self.start_button.clicked.connect(self.start)
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet('QPushButton{'
                                        'border: 2px solid black'
                                        'background-color: lightgrey;'
                                        '}'
                                        'QPushButton::disabled{'
                                        'border: 2px solid grey'
                                        '}'
                                        )

    def choose_difficulty(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.difficulty = radioButton.difficulty
            self.start_button.setEnabled(True)

    def start(self):

        self.mines = 0
        self.grid = []
        self.grid_x = 0
        self.grid_y = 0
        self.status = 'Playing'
        self.colors = {'': 'white', '1': 'blue', '2': 'green', '3': 'red', '4': 'darkblue',
                       '5': 'brown', '6': 'cyan', '7': 'purple', '8': 'grey', 'M': 'black'}
        self.bomb_icon = QIcon('./img/bomb.png')

        self.grid_generation()
        self.grid_buttons = [[QtWidgets.QPushButton(f'{self.grid[i][j]}',
                                                    self) for j in range(self.grid_x)] for i in range(self.grid_y)]
        self.mask_buttons = [[QtWidgets.QPushButton('',
                                                    self) for j in range(self.grid_x)] for i in range(self.grid_y)]
        self.setted_flags = self.mines
        self.title.hide()
        self.radiobutton_b.hide()
        self.radiobutton_i.hide()
        self.radiobutton_e.hide()
        self.start_button.hide()
        self.difficulty_label.hide()

        self.status_button = QtWidgets.QPushButton(self)
        self.status_button.setIcon(QIcon('./img/default_status.png'))
        self.status_button.setGeometry(int((self.width - 32) / 2), 20, 32, 32)
        self.status_button.setIconSize(QSize(25, 25))
        self.status_button.show()
        self.status_button.clicked.connect(self.start)

        self.timer = QTimer()
        self.time = QTime(0, 0, 0)

        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(1000)

        self.mines_counter = QtWidgets.QLabel(
            self, text=f'{self.setted_flags:03}')
        self.mines_counter.show()
        self.mines_counter.setGeometry(10, 20, 80, 32)
        self.mines_counter.setStyleSheet('background-color: black;'
                                         'text-align: right;'
                                         'color: red;'
                                         'font-size: 28px;'
                                         'border: 2px solid grey;'
                                         )
        self.mines_counter.setAlignment(
            Qt.AlignmentFlag.AlignRight)

        self.timer_label = QtWidgets.QLabel(
            self, text='00:00')
        self.timer_label.show()
        self.timer_label.setGeometry(self.width-90, 20, 80, 32)
        self.timer_label.setStyleSheet('background-color: black;'
                                       'text-align: right;'
                                       'color: red;'
                                       'font-size: 28px;'
                                       'border: 2px solid grey;'
                                       )

        for i in range(self.grid_y):
            for j in range(self.grid_x):
                self.grid_buttons[i][j].setGeometry(10 + j*25, 60+i*25, 25, 25)
                if self.grid_buttons[i][j].text() == '0':
                    self.grid_buttons[i][j].setText('')

                self.grid_buttons[i][j].show()
                self.grid_buttons[i][j].setStyleSheet(
                    'border: 1px solid grey;'
                    f'color: {self.colors[self.grid_buttons[i][j].text()]};'
                )

                if self.grid_buttons[i][j].text() == 'M':
                    self.grid_buttons[i][j].setIcon(self.bomb_icon)
                    self.grid_buttons[i][j].setIconSize(QSize(25, 25))
                    self.grid_buttons[i][j].setStyleSheet(
                        'border: 1px solid grey;'
                        'text-align: left;'
                        'font-size: 1px')
                self.mask_buttons[i][j].setGeometry(10 + j*25, 60+i*25, 25, 25)
                self.mask_buttons[i][j].setStyleSheet(
                    'QPushButton{'
                    'border-left: 1px solid black;'
                    'background-color: lightgrey;'
                    '}'
                    'QPushButton::disabled{'
                    'color: black;'
                    '}')
                self.mask_buttons[i][j].show()
                self.mask_buttons[i][j].setText('')
                self.mask_buttons[i][j].installEventFilter(self)

    def timerEvent(self):
        self.time = self.time.addSecs(1)
        self.timer_label.setText(self.time.toString("mm:ss"))

    # grid generation

    def grid_generation(self):
        match self.difficulty:
            case 'Beginner':
                self.width = 246
                self.height = 300
                self.grid_x = 9
                self.grid_y = 9
                self.mines = 10
            case 'Intermediate':
                self.width = 420
                self.height = 475
                self.grid_x = 16
                self.grid_y = 16
                self.mines = 40
            case 'Expert':
                self.width = 770
                self.height = 475
                self.grid_x = 30
                self.grid_y = 16
                self.mines = 100

        self.x = int((1920 - self.width) / 2)
        self.y = int((1080 - self.height) / 2)
        self.setFixedSize(self.width, self.height)
        self.setGeometry(self.x, self.y, self.width, self.height)

        self.grid = [[0 for _ in range(self.grid_x)]
                     for _ in range(self.grid_y)]

        for i in range(self.mines):

            row = random.randint(0, self.grid_y - 1)
            col = random.randint(0, self.grid_x - 1)

            while self.grid[row][col] == 'M':
                row = random.randint(0, self.grid_y - 1)
                col = random.randint(0, self.grid_x - 1)

            self.grid[row][col] = 'M'

            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (row+i < 0 or row+i >= self.grid_y) or (col+j < 0 or col+j >= self.grid_x):
                        continue
                    if self.grid[row+i][col+j] == 'M':
                        continue
                    self.grid[row+i][col+j] += 1

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.RightButton:

                if obj.isEnabled() == True and self.status == 'Playing':
                    self.set_flag(obj)
            elif event.button() == Qt.MouseButton.LeftButton:
                if obj.isEnabled() == True and self.status == 'Playing':
                    self.clear_cell(obj)
        return QObject.event(obj, event)

    def set_flag(self, obj):
        if obj.text() == '?':
            obj.setText('')
            self.setted_flags += 1
            self.mines_counter.setText(f'{self.setted_flags:03}')
        elif obj.text() != '?':
            if self.setted_flags > 0:
                obj.setText('?')
                for i in range(self.grid_y):
                    for j in range(self.grid_x):
                        if obj == self.mask_buttons[i][j]:
                            x = j
                            y = i
                if self.grid_buttons[y][x].text() == 'M':
                    self.mines -= 1
                self.setted_flags -= 1
                self.mines_counter.setText(f'{self.setted_flags:03}')
                self.game_win()

    def clear_cell(self, obj):
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                if obj == self.mask_buttons[i][j]:
                    x = j
                    y = i

        if obj.isHidden() == True:
            return

        if obj.text() != '?':
            obj.hide()

            if self.grid_buttons[y][x].text() == 'M':
                self.game_lost()

            if self.grid_buttons[y][x].text() == '':
                if y == 0:
                    self.clear_cell(obj=self.mask_buttons[y+1][x])
                    if x == 0:
                        self.clear_cell(obj=self.mask_buttons[y][x+1])
                    elif x == self.grid_x - 1:
                        self.clear_cell(obj=self.mask_buttons[y][x-1])
                    else:
                        self.clear_cell(obj=self.mask_buttons[y][x+1])
                        self.clear_cell(obj=self.mask_buttons[y][x-1])
                elif y == self.grid_y - 1:
                    self.clear_cell(obj=self.mask_buttons[y-1][x])
                    if x == 0:
                        self.clear_cell(obj=self.mask_buttons[y][x+1])
                    elif x == self.grid_x - 1:
                        self.clear_cell(obj=self.mask_buttons[y][x-1])
                    else:
                        self.clear_cell(obj=self.mask_buttons[y][x+1])
                        self.clear_cell(obj=self.mask_buttons[y][x-1])
                else:
                    self.clear_cell(obj=self.mask_buttons[y+1][x])
                    self.clear_cell(obj=self.mask_buttons[y-1][x])
                    if x == 0:
                        self.clear_cell(obj=self.mask_buttons[y][x+1])
                    elif x == self.grid_x - 1:
                        self.clear_cell(obj=self.mask_buttons[y][x-1])
                    else:
                        self.clear_cell(obj=self.mask_buttons[y][x+1])
                        self.clear_cell(obj=self.mask_buttons[y][x-1])

    def game_lost(self):
        self.status = 'Lost'
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                self.mask_buttons[i][j].hide()
        self.status_button.setIcon(QIcon('./img/lost_status.png'))
        self.status_button.setIconSize(QSize(25, 25))
        self.timer.stop()

    def game_win(self):
        if self.mines == 0:
            self.status = 'Won'
            self.status_button.setIcon(QIcon('./img/win_status.png'))
            self.status_button.setIconSize(QSize(25, 25))
            self.timer.stop()
            for i in range(self.grid_y):
                for j in range(self.grid_x):
                    if self.mask_buttons[i][j].text() != '?':
                        self.mask_buttons[i][j].hide()
                    else:
                        self.mask_buttons[i][j].setDisabled(True)


def application():
    app = QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    application()
