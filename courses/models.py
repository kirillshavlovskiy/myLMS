
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import TextField


class Code(models.Model):
    code = models.TextField()


class AI_Code(models.Model):
    Input_message = models.TextField()


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    structure = models.JSONField()  # This field will now store a list of module titles
    objective = models.TextField()
    num_lessons = models.IntegerField(default=0)  # New field for number of lessons
    num_tasks = models.IntegerField(default=0)  # New field for number of lessons

    def __str__(self):
        return self.title

class Module(models.Model):
    number = models.IntegerField()
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"Module {self.number}: {self.title}"


class Lesson(models.Model):
    number = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    def __str__(self):
        return f"Lesson {self.number}: {self.title}"


class Task(models.Model):
    task_name = models.CharField(max_length=100)
    description = models.TextField()
    correct_code = models.TextField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    def __str__(self):
        return self.task_name


class Task_thread(models.Model):
    thread_id = models.CharField(max_length=200)
    assistant_id = models.CharField(max_length=200)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    tasks_solved = models.IntegerField(default=0)
    runs = models.IntegerField(default=0)
    prompts = models.JSONField(default=dict)  # Thisfield will now store a list
    responses = models.JSONField(default=dict)  # This field will now store a list
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class TextContent(models.Model):
    content = models.TextField()


class CodeContent(models.Model):
    code = models.TextField()

