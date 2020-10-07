# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

import sys
import os
import re
import shutil
import sqlite3

from datetime import *
from time import strftime, time, sleep

import MainWindow
import NewTaskWindow

#MainWindow
#NewTask
#TaskDetails
#CompletedTasks

class Application(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.AddTask.triggered.connect(self.add_task)
		self.ActualTasks.triggered.connect(self.view_actual)
		self.CompletedTasks.triggered.connect(self.view_complited)
		self.MainTable.itemDoubleClicked.connect(self.open_info)
	
	def add_task(self):
		self.new_task = NewTask()
		self.new_task.show()
	
	def view_actual(self):
		pass
	
	def view_complited(self):
		pass
	
	def open_info(self):
		global id
		
		pass
	
	
	
class NewTask(QtWidgets.QMainWindow, NewTaskWindow.Ui_NewTaskWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)


class TaskDetails(QtWidgets.QMainWindow, TaskDetailsWindow.Ui_TaskDetailsWindow):
	def __init__(srlf):
		super().__init__()
		self.setupUi(self)



def main():

	global database
	global today
	
	database = r'tasks.db'
	today = datetime.now().strftime('%d.%m.%Y')
	
	app = QtWidgets.QApplication(sys.argv)
	window = Application()
	window.show()
	app.exec_()

if __name__ == '__main__':
	main()