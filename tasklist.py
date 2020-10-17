# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

import sys
import os
import re
import shutil
import sqlite3
import random

from datetime import *
from time import strftime, time, sleep

import MainWindow
import NewTaskWindow
import TaskDetailsWindow

#MainWindow
#NewTask
#TaskDetails
#CompletedTasks

class Application(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.preload()
		self.load_data(0)
		self.AddTask.triggered.connect(self.add_task)
		self.ActualTasks.triggered.connect(self.view_actual)
		self.CompletedTasks.triggered.connect(self.view_complited)
		self.MainTable.itemDoubleClicked.connect(self.open_info)

	def preload(self):
		self.MainTable.setColumnCount(6)
		self.MainTable.setRowCount(1)
		headers = ['ID', 'Создана', 'Дедлайн', 'Важность', 'Срочность', 'Название']
		self.MainTable.setHorizontalHeaderLabels(headers)
		header = self.MainTable.horizontalHeader()
		header.resizeSection(0, 10)
		header.resizeSection(1, 90)
		header.resizeSection(2, 90)
		header.resizeSection(3, 80)
		header.resizeSection(4, 80)
		header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

	def load_data(self, mode):
		self.MainTable.setRowCount(0)
		db_connector = sqlite3.connect(database)
		cursor = db_connector.cursor()
		query = 'SELECT ID, created, deadline, importance, urgency, name FROM tasks WHERE is_done = (?)'
		cursor.execute(query,(mode,))
		result = cursor.fetchall()
		if result:
			rows = len(result)
			self.MainTable.setRowCount(rows)
			for i in range(rows):
				for j in range(6):
					cell = QtWidgets.QTableWidgetItem()
					cell.setText(str(result[i][j]))
					cell.setFlags(QtCore.Qt.ItemIsEnabled)
					self.MainTable.setItem(i, j, cell)
		else:
			self.MainTable.setRowCount(1)
			for i in range(6):
				cell = QtWidgets.QTableWidgetItem()
				cell.setText('Empty DB')
				cell.setFlags(QtCore.Qt.ItemIsEnabled)
				self.MainTable.setItem(0, i, cell)
		cursor.close()
	
	def add_task(self):
		self.new_task = NewTask()
		self.new_task.show()
	
	def view_actual(self):
		self.load_data(0)
	
	def view_complited(self):
		self.load_data(1)
	
	def open_info(self):
		global id
		
		pass


class NewTask(QtWidgets.QMainWindow, NewTaskWindow.Ui_NewTaskWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.deadline_date.setDate(QtCore.QDate.currentDate())
		self.buttons.button(self.buttons.Cancel).setText('Отмена')
		self.cache()
		self.buttons.accepted.connect(self.add_task)
		self.buttons.rejected.connect(self.cancel)
	
	def cache(self):
		db_connector = sqlite3.connect(database)
		cursor = db_connector.cursor()
		query = 'SELECT name FROM (SELECT * FROM tasks WHERE is_done = 0) WHERE subtask_for = NULL'
		cached = cursor.fetchall()
		cursor.close()
		if cached:
			for i in range(len(cached)):
				self.select_main_task.addItem(cached[i][0])
		else:
			self.select_main_task.addItem('Empty DB')
	
	def add_task(self):
		today = datetime.now().strftime('%d.%m.%Y')
		db_connector = sqlite3.connect(database)
		cursor = db_connector.cursor()
		name = self.task_name.text()
		if not name:
			name = 'Без названия (' + str(random.randint(1, 10000)) + ')'
		details = self.task_details.toPlainText()
		temp = self.deadline_date.date()
		deadline = str(temp.toPyDate())[8:] + '.' + str(temp.toPyDate())[5:7] + '.' + str(temp.toPyDate())[0:4]
		importance = self.select_importance.currentText()
		urgency = self.select_urgency.currentText()
		if str(self.select_main_task.currentText()) == 'Не является подзадачей':
			subtask_for = None
		elif str(self.select_main_task.currentText()) == 'Empty DB':
			subtask_for = None
		else:
			main_task = str(self.select_main_task.currentText())
			cursor.execute('SELECT ID FROM tasks WHERE name = (?)', (main_task,))
			subtask_for = cursor.fetchall()
			subtask_for = int(str(subtask_for[0][0]))
		timer = 0
		clicks = 0
		is_done = 0
		params = (name, details, subtask_for, today, deadline, importance, urgency, timer, clicks, is_done)
		query = 'INSERT INTO tasks (name, details, subtask_for, created, deadline, importance, urgency, timer, clicks, is_done) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
		cursor.execute(query, params)
		db_connector.commit()
		cursor.close()
		window.load_data(0)
		self.close()
		
	def cancel(self):
		self.close()


class TaskDetails(QtWidgets.QMainWindow, TaskDetailsWindow.Ui_TaskDetailsWindow):
	def __init__(srlf):
		super().__init__()
		self.setupUi(self)



def main():

	global database
	global today
	global window
	
	database = r'tasks.db'
	today = datetime.now().strftime('%d.%m.%Y')
	
	app = QtWidgets.QApplication(sys.argv)
	window = Application()
	window.show()
	app.exec_()

if __name__ == '__main__':
	main()