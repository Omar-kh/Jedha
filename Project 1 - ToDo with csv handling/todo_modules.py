
# %%
import numpy as np
import pandas as pd
import uuid
import re
import datetime


# %%
str(uuid.uuid1().int)[:4]
"blabla".upper()


# %%
my_date = datetime.date(1990, 12, 28)
my_date.day

# %% [markdown]
# ### ToDo Controller

# %%
# Define the ToDo controller


class ToDo:
    def __init__(self):
        self.todo = []

    def get_task_by_id(self, task_id):
        return next((task for task in self.todo if task.id == task_id),
                    "This task does not seem to exist")

    def add_task(self, tasks):
        self.todo.extend(tasks)

    def remove_task(self, tasks):
        for task in tasks:
            self.todo.remove(task)

    def show_task(self, task_id):
        task = next((task for task in self.todo if task.id == task_id),
                    "This task does not seem to exist")
        for task_attr, task_value in task.__dict__.items():
            print(f"{task_attr}: {task_value}")

    def load_tasks(self, tasks_path):
        dataset = pd.read_csv(tasks_path)
        self.todo = [Task(dataset.loc[i, 'title'],
                          dataset.loc[i, 'due_date'],
                          dataset.loc[i, 'end_date'],
                          dataset.loc[i, 'status']) for i in range(len(dataset))]

    def save_tasks(self, file_path):
        todo_dataframe = pd.DataFrame([vars(task) for task in self.todo])
        todo_dataframe.to_csv(file_path)

# %% [markdown]
# ### Task Controller

# %%
# Define the task controller


class Task:
    def __init__(self, title, due_date="Not specified", end_date="Not specified", status="Created"):
        self.id = str(uuid.uuid1().int)[-6:]
        self.title = title
        self.status = status
        self.due_date = due_date
        self.end_date = end_date

    def rename_task(self, new_title):
        self.title = new_title

    def update_task(self):
        self.status = "Updated"

    def close_task(self):
        self.status = "Closed"
        self.end_date = datetime.datetime.today().strftime("%d/%m/%y")

    def change_date(self, new_date):
        self.due_date = new_date


# %% [markdown]
# ### Terminal Controller
# #### Needs optimization

# %%
# Define the command line controller
class Terminal:
    def __init__(self):
        self.commands = ["add", "complete", "delete",
                         "rename", "chdate", "show", "load", "save", "quit"]

    def process_input(self, usr_input):
        command = ''
        args = []
        split_input = []

        if len(usr_input) == 0:
            print("No command typed")

        if len(usr_input) > 0:
            split_input = usr_input.split(' ')
            command = split_input[0]
            command = self.validate_command(command)

        if len(split_input) > 1:
            split_args = split_input[1:]
            args = ' '.join(split_args)
            args = args.split(',')
            args = [arg.strip() for arg in args]

        command, args = self.validate_args(command, args)
        return command, args

    def validate_command(self, command):
        if command not in self.commands:
            print("Command not found")
            command = "Not found"
        return command

    def validate_args(self, command, args):
        if command.lower() not in ["quit", "save", "load"] and command.lower() in self.commands and len(args) == 0:
            print("You didn't type any arguments, please type them")
            command = ''
        return command, args

    def add_task(self, todo, tasks):
        tasks_obj = [Task(task) for task in tasks]
        todo.add_task(tasks_obj)
        created_tasks = [(task.id, task.title) for task in todo.todo]
        return input(f"You successfully added the following tasks {created_tasks}. What would you like to do next?")

    def remove_task(self, todo, tasks_ids):
        tasks_to_remove = []
        for task_id in tasks_ids:
            task = todo.get_task_by_id(task_id)
            if type(task) == str:
                break
            else:
                tasks_to_remove.append((task.id, task.title))
                todo.remove_task([task])

        if len(tasks_to_remove) < len(tasks_ids):
            return input(f"Could not remove your tasks. One of the ids didn't match. Please retype the command with all the correct ids")

        return input(f"Successfully removed the following tasks: {tasks_to_remove}. What else would you like to do?")

    def show_task(self, todo, tasks_ids):
        tasks_to_show = []
        if tasks_ids[0] == 'all':
            print("Here are all your tasks")
            for task in todo.todo:
                todo.show_task(task.id)
            return input("What else would you like to do?")
        else:
            for task_id in tasks_ids:
                task = todo.get_task_by_id(task_id)
                if type(task) == str:
                    break
                else:
                    tasks_to_show.append(task_id)

            if len(tasks_to_show) < len(tasks_ids):
                return input(f"Could not show your tasks. One of the ids didn't match. Please retype the command with all the correct ids")

            print("Here are the tasks you wanted to see:")
            for task_id in tasks_to_show:
                todo.show_task(task_id)
            return input("What else would you like to do?")

    def complete_task(self, todo, tasks_ids):
        tasks_to_complete = []
        for task_id in tasks_ids:
            task = todo.get_task_by_id(task_id)
            if type(task) == str:
                break
            else:
                tasks_to_complete.append((task.id, task.title))
                task.close_task()

        if len(tasks_to_complete) < len(tasks_ids):
            return input(f"Could not complete your tasks. One of the ids didn't match. Please retype the command with all the correct ids")

        return input(f"Successfully completed the following tasks: {tasks_to_complete}. What else would you like to do?")

    def rename_task(self, todo, tasks_ids):
        task = todo.get_task_by_id(tasks_ids[0])
        if type(task) == str:
            return input(f"{task}. Please retry typing the command with the correct Id")
        old_title = task.title
        new_title = input(
            f"You choose the task {old_title}. Please type the new title for your task:")
        task.rename_task(new_title)
        task.update_task()
        return input(f"You successfully renamed the task id {task.id} from '{old_title}' to '{task.title}'. What else would you like to do?")

    def update_date(self, todo, tasks_ids):
        task = todo.get_task_by_id(tasks_ids[0])
        if type(task) == str:
            return input(f"{task}. Please retry typing the command with the correct Id")
        date = input("Please type a date in the format: dd/mm/yyyy")
        new_date = self.process_date(date)
        if new_date == "The date format doesn't seem to be correct":
            return input(f"{new_date}. Please retry with a correct date format")
        task.change_date(new_date.strftime("%d/%m/%y"))
        task.update_task()
        return input(f"You successfully set the date for the task {task.title} to {task.due_date}. What else would you like to do?")

    def process_date(self, date):
        date_arr = date.split('/')
        print(date_arr)
        if len(date_arr) != 3:
            return "The date format doesn't seem to be correct"
        try:
            date_arr = [int(elem) for elem in date_arr]
            print(date_arr)
            new_date = datetime.date(date_arr[2], date_arr[1], date_arr[0])
            return new_date
        except:
            return "The date format doesn't seem to be correct"

    def save_todo(self, todo):
        file_path = input("Please give a name to your file (e.g. my_todo.csv)")
        todo.save_tasks(file_path)
        return input(f"Successfully saved your file to {file_path}. What else would you like to do?")

    def load_todo(self, todo):
        file_path = input(
            "Please type the relative path to your file (e.g. './my_todo.csv')")
        todo.load_tasks(file_path)
        print("Successfully loaded your file")
        return self.show_task(todo, ['all'])

    def start_app(self):
        user_todo = ToDo()
        command = ''
        user_choice = input("Please choose according to your need")

        while(command.lower() != "quit"):

            command, args = self.process_input(user_choice)

            if command.lower() == "add":
                user_choice = self.add_task(user_todo, args)

            if command.lower() == "complete":
                user_choice = self.complete_task(user_todo, args)

            if command.lower() == "delete":
                user_choice = self.remove_task(user_todo, args)

            if command.lower() == "rename":
                user_choice = self.rename_task(user_todo, args)

            if command.lower() == "chdate":
                user_choice = self.update_date(user_todo, args)

            if command.lower() == "show":
                user_choice = self.show_task(user_todo, args)

            if command.lower() == "load":
                user_choice = self.load_todo(user_todo)

            if command.lower() == "save":
                user_choice = self.save_todo(user_todo)

            if command == "Not found" or command == '':
                user_choice = input('Choose again')

        print("Program closed")
