import re
import logging
import subprocess
import json
import os
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from openai import OpenAI

from .forms import ContentForm, CodeForm
from django.shortcuts import get_object_or_404, redirect, render
from .models import Course, Module, Lesson, Task, Task_thread
from .openai_service import generate_lesson_content, generate_project_content, assistant_thread_run, message_loop, \
    assistant_preprocess_task


client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

#Enable logging
#logging.basicConfig(level=logging.DEBUG)


def execute_python_code(code, input_values):

    try:
        # Define the execute_python_code function with inputs
        command = ["python3", "-c", code]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        input_data = '\n'.join(input_values).encode()  # Concatenate input values
        output, error = process.communicate(input=input_data)

        output_str: str = output.decode("utf-8")
        error_str: str = error.decode("utf-8")
        completion_status = int(process.poll())
        print('completion status', completion_status)
        line_number = None
        error_lines = error_str.split('\n')
        while error_lines and not error_lines[-1]:
            error_lines.pop()
        last_line = error_lines[-1] if error_lines else ''
        if "EOFError: EOF when reading a line" in error_str:
            pattern = r'File ".+?", line (\d+), in <module>'
            completion_status = None
            # Check if there are enough lines in the error message
            if len(error_lines) > 1:
                for line in error_lines:
                    match = re.search(pattern, line)
                    if match:
                        line_number = int(match.group(1)) - 1
                        logging.error("Code execution interrupted by input request: ", error_str, 'on the line ',
                                      line_number)
                        break
            return output_str, completion_status, line_number, last_line
        elif error_str:
            print("check")
            pattern = r'File ".+?", line (\d+)'
            if len(error_lines) > 1:
                for line in error_lines:
                    match = re.search(pattern, line)
                    if match:
                        line_number = int(match.group(1)) - 1
                        print("Line number with error:", line_number)
                        logging.error("An error occurred during code execution: %s", last_line)
                        break
                # Return output instead of the error message
                return error_str, completion_status, line_number, last_line
        else:
            logging.debug("Python code execution successful. Output: %s", output_str)
            return output_str, completion_status, line_number, last_line

    except subprocess.TimeoutExpired:
        output_str = "Code execution timed out."
        logging.error("Code execution timed out.")
        return output_str

    except Exception as e:
        output_str = str(e)
        logging.error("An error occurred: %s", e)
        return output_str


def extract_input_prompt(code, line):
    return code.split('\n')[line].split("input(", 1)[1].split(")", 1)[0].strip().strip('"').strip("'")


@csrf_exempt
def lesson_process_code(request, lesson_id):
    print('check if code run started on the server')
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    tasks = Task.objects.filter(lesson_id=lesson.id)
    if request.method == 'POST':
        form = CodeForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            input_values = request.POST.getlist('input_value')
            symbols_processed = str(request.POST.get('symbols_processed', ''))
            try:
                output, complete, prompt_line_n, message = execute_python_code(code, input_values)
                print("output: ", output, "complete", complete, "prompt", prompt_line_n, 'message', message)
                # Truncate output based on the pattern match
                output_clean: str = output[
                                    len(symbols_processed):]  # Truncate the output based on symbol processed length
                if complete == None:
                    return JsonResponse(
                        {'input_requested': True,
                         'prompt_message': prompt_line_n,
                         'output': output_clean,
                         })
                elif complete > 0:
                    completion_status = complete == 0
                    return JsonResponse(
                        {
                            'prompt_message': prompt_line_n,
                            'output': output_clean,
                            'completed': completion_status,
                            'message': message})
                else:
                    completion_status = complete == 0
                    return JsonResponse({'output': output_clean, 'completed': completion_status, })
            except Exception as e:
                error_msg = "An error occurred during code execution: {}".format(str(e))
                logging.error(error_msg)
                return JsonResponse({'error': error_msg})
    else:
        form = CodeForm()

    return render(request, "courses/Show_lesson_process_page.html", {
        'form': form,
        'tasks': tasks,
        'lesson': lesson
    })


def retrieve_thread(request):
    try:
        print('Log: start_thread retrieve:')
        if request.method == 'POST':
            task_id = request.POST.get('task_id')
            print(task_id)
            task_thread = Task_thread.objects.filter(task_id=task_id).last()
            messages = client.beta.threads.messages.list(thread_id=task_thread.thread_id)
            print("messages: ", messages)
            return JsonResponse(
                {'messages': messages})
        else:
            # Handle the case when the form is not valid
            print("Form is not valid")
            return JsonResponse({'error': 'Form is not valid'})
    except Exception as e:
        # Handle any exception that occurred

        print('error', str(e))
        return JsonResponse({'error:': str(e)})


def save_thread(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        thread = request.POST.get('thread')
        code = request.POST.get('code')
        task_thread = Task_thread.objects.filter(task_id=task_id).last()
        task_thread.learning_thread += [thread]
        task_thread.code = code
        task_thread.save()
        return JsonResponse({'system_message': 'saved'})
    else:
        # Handle the case when the form is not valid
        print("Form is not valid")
        return JsonResponse({'error': 'Form is not valid'})


def start_thread(request):
    try:
        print('start_thread:')
        if request.method == 'POST':
            task_id = request.POST.get('task_id')
            code = request.POST.get('code')
            print(task_id)
            task = get_object_or_404(Task, id=task_id)
            assistant_id = 'asst_Kx2zKp0x0r3fLA6ZFiIGVsPZ'
            print(code)
            if not Task_thread.objects.filter(task=task).exists():
                thread = client.beta.threads.create()
                task_thread = Task_thread.objects.create(thread_id=thread.id,
                                                         assistant_id=assistant_id,
                                                         task=task)
                task_thread.save()
                thread_id = task_thread.thread_id
                prompt_1 = 'There is a task: ' + str(task.description)
                prompt_2 = '\nFor the following code, please provide a detailed explanation starting from topic basics on how we should approach coding task completion:\n' + str(
                    code)
                message = f"{prompt_1} {prompt_2} "
                print(task_thread)
                AI_response = message_loop(message, assistant_id, thread_id)
                print("AI_response: ", AI_response)
                return JsonResponse(
                    {'ai_response': AI_response, 'thread_id': thread_id, 'task_description': task.description})
            else:
                task_thread = Task_thread.objects.filter(task_id=task_id).last()
                messages = task_thread.learning_thread[-1]
                print("messages: ", messages)
                return JsonResponse({'messages': messages, 'thread_id': task_thread.thread_id})
        else:
            # Handle the case when the form is not valid
            print("Form is not valid")
            return JsonResponse({'error': 'Form is not valid'})
    except Exception as e:
        # Handle any exception that occurred

        print('error', str(e))
        return JsonResponse({'error': str(e)})


def chat(request):
    try:
        if request.method == 'POST':
            message = request.POST.get('input_message')
            thread_id = request.POST.get('thread_id')
            if not thread_id:
                thread = client.beta.threads.create()
                thread_id = thread.id
            assistant_id = 'asst_Kx2zKp0x0r3fLA6ZFiIGVsPZ'
            AI_response = message_loop(message, assistant_id, thread_id)
            print("AI_response: ", AI_response)
            return JsonResponse({'ai_response': AI_response, 'thread_id': thread_id})
        else:
            # Handle the case when the form is not valid
            print("Form is not valid")
            return JsonResponse({'error': 'Form is not valid'})

    except Exception as e:
        # Handle any exception that occurred
        print('error', str(e))
        return JsonResponse({'error': str(e)})


def code_process_ai(request):
    try:
        if request.method == 'POST':
            print('code_process_123:')
            code = request.POST.get('code')
            output = request.POST.get('output')
            thread_id = request.POST.get('thread_id')
            task_id = request.POST.get('task_id')
            print(task_id)
            task = get_object_or_404(Task, id=task_id)
            print('task id found: ', task_id)
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id
            if task_id:
                result = assistant_preprocess_task(code, output, thread_id, task.description)
                if result is not None and len(result) == 3:
                    ai_response, assistant_id, thread_id = result
                    assistant_id = 'asst_Kx2zKp0x0r3fLA6ZFiIGVsPZ'
                    return JsonResponse(
                        {'ai_response': ai_response, 'thread_id': thread_id, 'assistant_id': assistant_id,
                         'task_description': task.description})
                else:
                    # Handle the case when the result does not contain the expected values
                    print("Error: Incorrect number of values returned from assistant_thread_run")
                    return JsonResponse({'error': 'Incorrect number of values returned'})
            else:
                result = assistant_thread_run(code, output, thread_id)
                if result is not None and len(result) == 3:
                    ai_response, assistant_id, thread_id = result
                    assistant_id = 'asst_Kx2zKp0x0r3fLA6ZFiIGVsPZ'
                    return JsonResponse(
                        {'ai_response': ai_response, 'thread_id': thread_id, 'assistant_id': assistant_id})
                else:
                    # Handle the case when the result does not contain the expected values
                    print("Error: Incorrect number of values returned from assistant_thread_run")
                    return JsonResponse({'error': 'Incorrect number of values returned'})
        return JsonResponse({'error': 'Form is not valid'})
    except Exception as e:
        # Handle any exception that occurred
        print('error_0', str(e))
        return JsonResponse({'error_0': str(e)})


def content_process_form(request, content_id):
    course = get_object_or_404(Course, pk=content_id)
    modules = Module.objects.filter(course_id=content_id)
    return render(request, 'courses/Course_module_list.html', {'course': course,
                                                               'modules': modules})


def display_content(request):
    # Fetch all the saved content from the database
    courses = Course.objects.all().order_by('-id')  # Newest first

    return render(request, 'courses/Show_courses_list.html', {'courses': courses})


def create_course_structure(request, course):
    file_path = os.path.join(settings.BASE_DIR, 'static/data/Basics.json')
    created_modules = []

    with open(file_path, 'r') as file:
        json_data = json.load(file)

    for module_data in json_data:
        module = Module.objects.create(number=module_data['number'], title=module_data['title'], course=course)
        # Collect the created module
        i = 0
        created_lessons = []
        for lesson_data in module_data['lessons']:
            if i != len(module_data['lessons']):
                print(len(module_data['lessons']))
                i += 1
                lesson = Lesson.objects.create(module=module, number=lesson_data['number'], title=lesson_data['title'])
                created_tasks = []
                for task in lesson_data['tasks']:
                    task_description = task['description'] + task['example_code']
                    task_question, task_code = generate_lesson_content(task_description)
                    task = Task.objects.create(lesson=lesson, task_name=task['task_title'],
                                               description=task['description'], correct_code=task_code)
                    created_tasks.append([task.description, task.correct_code])
                    created_lessons.append([lesson_data['title'], [created_tasks]])
                    task.save()
                created_modules.append(created_lessons)
                lesson.save()
            else:

                module_descr = ''
                for item in created_modules[-1]:
                    module_descr.join(item[0])

                project_title = module.title + ' Module Project Assignment'
                lesson = Lesson.objects.create(module=module, number=lesson_data['number'], title=project_title)
                project_code, project_description = generate_project_content(module_descr)

                task = Task.objects.create(lesson=lesson, task_name=task['task_title'],
                                           description=project_description, correct_code=project_code)
                created_tasks.append([task.description, task.code, ])
                created_lessons.append(created_tasks)
                task.save()
                lesson.save()
                print(task)
                print(lesson)
        created_modules.append(created_lessons)
        module.save()

        return created_modules


def create_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            new_course_name = form.cleaned_data['title']
            objective = form.cleaned_data['objective']
            description = form.cleaned_data['description']

            if not new_course_name:
                form.add_error(None, 'Failed to generate content.')
            else:
                new_course = Course.objects.create(title=new_course_name,
                                                   description=description,
                                                   objective=objective,
                                                   structure=[])

                new_course.structure = create_course_structure(request, new_course)
                new_course.save()
                return redirect('display_content')  # Redirect to a new URL
    else:
        form = ContentForm()
    return render(request, 'courses/Show_content_generation_form.html', {'form': form})
