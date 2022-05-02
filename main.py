import os
import sys, time, random

from zipfile import ZipFile

from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon
from PyQt6 import uic, QtGui, QtCore, QtWidgets

from threading import Thread
from pathlib import Path


sys.setrecursionlimit(5000)

uifile = 'sudoku.ui'
form, base = uic.loadUiType(uifile)

PATH = 'data'
print(os.path.isdir(PATH))
if not os.path.isdir(PATH):
	with ZipFile('data.zip', 'r') as zip_ref:
		zip_ref.extractall(PATH)

class DifficultyDialog(QDialog):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("DifficultyDialog")
		self.setWindowIcon(QtGui.QIcon('assets/icons/question-mark.png'))

		self.difficulty = 'trivial'

		self.btn_trivial = QtWidgets.QPushButton("Trivial")
		self.btn_easy = QtWidgets.QPushButton("Easy")
		self.btn_medium = QtWidgets.QPushButton("Medium")
		self.btn_hard = QtWidgets.QPushButton("Hard")

		self.layout = QVBoxLayout()
		message = QLabel("Select a difficulty : ")
		self.layout.addWidget(message)
		self.layout.addWidget(self.btn_trivial)
		self.layout.addWidget(self.btn_easy)
		self.layout.addWidget(self.btn_medium)
		self.layout.addWidget(self.btn_hard)

		self.setLayout(self.layout)

		self.btn_trivial.clicked.connect(self.trivial)
		self.btn_easy.clicked.connect(self.easy)
		self.btn_medium.clicked.connect(self.medium)
		self.btn_hard.clicked.connect(self.hard)


	def trivial(self) -> None:
		self.close()
		self.difficulty = 'trivial'
	def easy(self) -> None:
		self.close()
		self.difficulty = 'easy'
	def medium(self) -> None:
		self.close()
		self.difficulty = 'medium'
	def hard(self) -> None:
		self.close()
		self.difficulty = 'hard'

class MainWindow(base, form):
	def __init__(self):
		super(base, self).__init__()
		self.setWindowIcon(QtGui.QIcon('assets/icons/sudoku.png'))

		self.PATHS = {
			"trivial": "data/puzzles0_kaggle",
			"easy": "data/puzzles2_17_clue",
			"medium": "data/puzzles3_magictour_top1465",
			"hard": "data/puzzles6_forum_hardest_1106",
		}
		self.DIFFICULTY = 'easy'

		self.board = None

		self.setupUi(self)
		self.setWindowTitle("Sudoku")

		self.setFixedHeight(500)
		self.setFixedWidth(440)

		self.actionNew_game.triggered.connect(self.resetBoard)

		self.actionSolve.triggered.connect(self.solveSudokuThread)
		self.actionShow_Backtracking_Slow.triggered.connect(self.solveSudokuThreadSlow)

		self.actionClear.triggered.connect(self.clearSudokuThread)
		self.actionAbout.triggered.connect(self.aboutSection)

		self.pushButtonReset.clicked.connect(self.resetSudokuThread)
		self.pushButtonCheck.clicked.connect(self.checkSudoku)

		self.createGame()

	def fixBox(self, i, j, index):
		getattr(self, f"comboBox_{i}_{j}").setCurrentIndex(index)
		getattr(self, f"comboBox_{i}_{j}").setEnabled(False)

	def enableBox(self, i, j):
		getattr(self, f"comboBox_{i}_{j}").setEnabled(True)

	def setBoxData(self, i, j, data):
		getattr(self, f"comboBox_{i}_{j}").setCurrentIndex(data)

	def getBoxDataIndex(self, i, j) -> int:
		return getattr(self, f"comboBox_{i}_{j}").currentIndex()

	def isBoxEnabled(self, i, j) -> bool:
		return getattr(self, f"comboBox_{i}_{j}").isEditable()

	def reset(self):
		self.clear()
		self.createSudoku(self.board)

	def clear(self):
		for i in range(9):
			for j in range(9):
				self.setBoxData(i, j, 0)
				self.enableBox(i, j)

	def solve(self, ms = 0) -> bool:
		for i in range(9):
			for j in range(9):
				if self.getBoxDataIndex(i, j) == 0:
					for val in range(1, 10):

						time.sleep(ms)
						if self.check(i, j, val):
							self.setBoxData(i, j, val)
							if self.solve(ms):
								return True
							self.setBoxData(i, j, 0)
					return False
		return True

	def check(self, i, j, val):
		if val == 0:
			return False

		for ii in range(9):
			if self.getBoxDataIndex(i, ii) == val:
				return False
			if self.getBoxDataIndex(ii, j) == val:
				return False
		x, y = i - i%3, j - j%3
		for ii in range(3):
			for jj in range(3):
				if self.getBoxDataIndex(x + ii, y + jj) == val:
					return False
		return True

	def showMessageBox(self, title, message):
		dlg = QMessageBox(self)
		dlg.setWindowTitle(title)
		dlg.setText(message)
		button = dlg.exec()

	def showDifficultySettings(self):
		diff = DifficultyDialog()
		diff.exec()
		if self.DIFFICULTY != diff.difficulty:
			self.DIFFICULTY = diff.difficulty
			self.boards = self.getSudokuData(self.PATHS[self.DIFFICULTY])
		self.boards = self.getSudokuData(self.PATHS[self.DIFFICULTY])

	def checkSudoku(self):
		solved = True
		for i in range(9):
			for j in range(9):

				val = self.getBoxDataIndex(i, j)
				self.setBoxData(i, j, 0)

				if not self.check(i, j, val):
					solved = False
					break

				self.setBoxData(i, j, val)

		if not solved:
			self.showMessageBox("Sudoku not solved", "Sudoku is either incomplete/incorrect !")
		else:
			self.showMessageBox("Congratulations !", "You have solved it correctly !")
			self.createGame()

	def solveSudoku(self, ms=0):
		self.pushButtonReset.setEnabled(False)
		self.actionClear.setEnabled(False)
		self.actionSolve.setEnabled(False)
		self.actionNew_game.setEnabled(False)
		self.actionShow_Backtracking_Slow.setEnabled(False)

		solvable = self.solve(ms)

		self.pushButtonReset.setEnabled(True)
		self.actionClear.setEnabled(True)
		self.actionSolve.setEnabled(True)
		self.actionShow_Backtracking_Slow.setEnabled(True)
		self.actionNew_game.setEnabled(True)

	def solveSudokuThread(self):
		self.setFocus()
		self.pushButtonReset.setEnabled(False)
		thread = Thread(target=self.solveSudoku)
		thread.start()

	def solveSudokuThreadSlow(self):
		self.setFocus()
		self.pushButtonReset.setEnabled(False)
		thread = Thread(target=self.solveSudoku, args = [0.001])
		thread.start()

	def clearSudokuThread(self):
		self.setFocus()
		thread = Thread(target=self.clear)
		thread.start()

	def resetSudokuThread(self):
		self.setFocus()
		thread = Thread(target=self.reset)
		thread.start()

	def resetBoard(self):
		self.createGame()

	def aboutSection(self):
		self.showMessageBox("About", """
This is a sudoku app made in Python using PyQt6.
(Currently under development)

Creator : Utkarsh Sharma
									 """)

	def createSudoku(self, board):
		if board is None: return None
		self.board = board
		dataList = self.toDataList(board)
		for row, col, val in dataList:
			self.fixBox(row, col, val)

	def toDataList(self, board):
		data = []
		for i in range(9):
			for j in range(9):
				if board[i][j] != ".":
					data.append( (i, j, int(board[i][j])) )
		return data

	def getSudokuData(self, path):
		sdkList = []
		with open(path) as f:
			for line in f:
				mat = [['.' for i in range(9)] for i in range(9)]
				line = line.replace('/n', '')
				if len(line)==82:
					for i in range(81):
						mat[i//9][i%9] = line[i]
				sdkList.append(mat)
		return sdkList

	def createGame(self):
		self.showDifficultySettings()
		self.clear()
		index = random.randint(0, len(self.boards))
		self.board = self.boards[index]
		self.createSudoku(self.board)

def main():
	app = QApplication(sys.argv)

	window = MainWindow()
	window.show()
	sys.exit(app.exec())

if __name__ == '__main__':
	main()