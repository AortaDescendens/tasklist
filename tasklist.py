# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

import sys
import os
import re
import shutil
import sqlite3
import random

from datetime import *
from time import strftime, time, sleep, gmtime

import MainWindow
import NewTaskWindow
import TaskDetailsWindow


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
		index = self.MainTable.currentItem().row()
		id = self.MainTable.item(index, 0).text()
		self.task_details = TaskDetails()
		self.task_details.show()


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
		cursor.execute('SELECT id, name FROM (SELECT * FROM tasks WHERE is_done = 0) WHERE subtask_for = 0')
		cached = cursor.fetchall()
		cursor.close()
		if cached:
			for i in range(len(cached)):
				self.select_main_task.addItem(str(cached[i][0]) + '. ' + cached[i][1])
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
		current_deadline = date(int(deadline.split('.')[2]), int(deadline.split('.')[1]), int(deadline.split('.')[0]))
		diff = current_date - current_deadline
		try:
			if int(str(diff).split(' ')[0]) > 0:
				deadline = today
		except ValueError:
			pass
		importance = self.select_importance.currentText()
		urgency = self.select_urgency.currentText()
		if str(self.select_main_task.currentText()) == 'Не является подзадачей':
			subtask_for = 0
		elif str(self.select_main_task.currentText()) == 'Empty DB':
			subtask_for = 0
		else:
			main_task = str(self.select_main_task.currentText()).split('. ')
			subtask_for = int(str(main_task[0]))
		timer = 0
		clicks = 0
		if (importance == 'Низкая') and (urgency == 'Низкая'):
			is_done = 1
		else:
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
	
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		timer_exec = False
		self.load_data()
		self.close_task_button.clicked.connect(self.close_task)
		self.click_button.clicked.connect(self.clicker)
		self.start_pause_button.clicked.connect(self.timer)
		self.null_button.clicked.connect(self.null_timer)
	
	def load_data(self):
#		timer_exec = False
		db_connector = sqlite3.connect(database)
		cursor = db_connector.cursor()
		query = 'SELECT * FROM tasks WHERE ID = (?)'
		cursor.execute(query,(id,))
		result = cursor.fetchall()[0]
		self.task_name.setText(result[1])
		if result[3] == 0:
			if result[2]:
				details_text = result[2] + '\n\n' + 'Создана: ' + result[4] + '\n' + 'Дедлайн: ' + result[5] + '\n' + 'Важность: ' + result[6] + '\n' + 'Срочность: ' + result[7]
			else:
				details_text = 'Нет описания\n\n' + 'Создана: ' + result[4] + '\n' + 'Дедлайн: ' + result[5] + '\n' + 'Важность: ' + result[6] + '\n' + 'Срочность: ' + result[7]
			cursor.execute('SELECT id, name, is_done FROM tasks WHERE subtask_for = (?)', (result[0],))
			subtasks = cursor.fetchall()
			if subtasks:
				details_text = details_text + '\n\nПодзадачи:\n'
				for i in range(len(subtasks)):
					details_text = details_text + '\t' + str(subtasks[i][0]) + '. ' + subtasks[i][1]
					if subtasks[i][2] == 1:
						details_text = details_text + ' - завершена\n'
					else:
						details_text = details_text + '\n'
		else:
			if result[2]:
				details_text = result[2] + '\n\n' + 'Создана: ' + result[4] + '\n' + 'Дедлайн: ' + result[5] + '\n' + 'Важность: ' + result[6] + '\n' + 'Срочность: ' + result[7]
			else:
				details_text = 'Нет описания\n\n' + 'Создана: ' + result[4] + '\n' + 'Дедлайн: ' + result[5] + '\n' + 'Важность: ' + result[6] + '\n' + 'Срочность: ' + result[7]
			cursor.execute('SELECT name FROM tasks WHERE ID = (?)', (result[3],))
			maintask = cursor.fetchall()[0]
			details_text = details_text + '\n\nПодзадача для:\n' + '\t' + str(result[3]) + '. ' + str(maintask[0])
		self.task_details.setText(details_text)
		self.timer_label.setText(strftime("%H:%M:%S", gmtime(result[8])))
		self.clicks_label.setText(str(result[9]))
		cursor.close()
		if result[10] == 1:
			self.close_task_button.setEnabled(False)
			self.click_button.setEnabled(False)
			self.start_pause_button.setEnabled(False)
			self.null_button.setEnabled(False)

	def clicker(self):
		db_connector = sqlite3.connect(database)
		cursor = db_connector.cursor()
		query = 'SELECT clicks FROM tasks WHERE ID = (?)'
		cursor.execute(query,(id,))
		clicks = cursor.fetchall()[0][0]
		clicks += 1
		self.clicks_label.setText(str(clicks))
		cursor.execute('UPDATE tasks SET clicks = (?) WHERE ID = (?)',(clicks, id))
		db_connector.commit()
		cursor.close()
		
	def timer(self, timer_exec):
#		print(timer_exec)
#		timer_exec = not timer_exec
#		if timer_exec == True:
#			print(timer_exec)
#			self.start_pause_button.setText('Стоп')
#			print('button')
#			db_connector = sqlite3.connect(database)
#			cursor = db_connector.cursor()
#			query = 'SELECT timer FROM tasks WHERE ID = (?)'
#			cursor.execute(query,(id,))
#			result = cursor.fetchall()
#			sec = int(cursor.fetchall()[0][0])
#			print(result)
#			sec = int(result[0][0])
#			print(sec)
#			while timer_exec:
#				self.clicks_label.setText(str(strftime("%H:%M:%S", gmtime(sec))))
#				sec += 1
#				sleep(1)
		pass
	
	def null_timer(self):
		pass
	
	def close_task(self):
		db_connector = sqlite3.connect(database)
		cursor = db_connector.cursor()
		cursor.execute('SELECT name FROM tasks WHERE ID = (?)', (id,))
		name = str(cursor.fetchall()[0][0])
		name += ' | Выполнено'
		cursor.execute('SELECT id, name FROM tasks WHERE subtask_for = (?)', (id,))
		subtasks = cursor.fetchall()
		query = 'UPDATE tasks SET name = (?), is_done = (?) WHERE ID = (?)'
		cursor.execute(query,(name, 1, id))
		if subtasks:
			for i in range(len(subtasks)):
				new_name = str(subtasks[i][1]) + ' | Выполнено'
				cursor.execute(query,(new_name, 1, subtasks[i][0]))
		db_connector.commit()
		cursor.close()
		window.load_data(0)
		self.close()


def main():

	global database
	global today
	global window
	global current_date
	
	database = r'tasks.db'
	today = datetime.now().strftime('%d.%m.%Y')
	current_date = today.split('.')
	current_date = date(int(current_date[2]), int(current_date[1]), int(current_date[0]))

	db_connector = sqlite3.connect(database)
	cursor = db_connector.cursor()
	cursor.execute('SELECT ID, deadline FROM tasks')
	result = cursor.fetchall()
	for i in range(len(result)):
		temp = result[i][1].split('.')
		current_deadline = date(int(temp[2]), int(temp[1]), int(temp[0]))
		diff = current_date - current_deadline
		try:
			if int(str(diff).split(' ')[0]) > 0:
				cursor.execute('UPDATE tasks SET deadline = (?) WHERE ID = (?)', (today, result[i][0]))
				db_connector.commit()
		except ValueError:
			pass
	cursor.close()
	
	app = QtWidgets.QApplication(sys.argv)
	window = Application()
	window.show()
	app.exec_()

if __name__ == '__main__':
	main()