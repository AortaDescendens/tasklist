# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
import re
import shutil
import sqlite3

#MainWindow
#NewTask
#TaskDetails
#CompletedTasks

class Aplication(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		

def main():
	global database
	database = r'tasks.db'
	app = QtWidgets.QApplication(sys.argv)
	window = Application()
	window.show()
	app.exec_()

if __name__ == '__main__':
	main()