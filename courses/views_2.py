import json
import logging
import subprocess
import sys
from io import StringIO

import openai
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from openai import OpenAI

from .forms import ContentForm, GeneratedContentForm, CodeForm
from django.shortcuts import get_object_or_404, redirect, render
from .models import GeneratedContent, Course, Lesson, Task
from .openai_service import generate_description, generate_lesson_content, generate_structure, generate_lesson_title, \
    re_generate_content

client = OpenAI()

# Enable logging
logging.basicConfig(level=logging.DEBUG)


# Define the execute_python_code function with inputs
def execute_python_code(code, input_values):


    try:
        command = ["python", "-c", code]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        input_data = '\n'.join(input_values)  # Concatenate input values
        output, error = process.communicate(input=input_data.encode())

        output_str: str = output.decode("utf-8")
        error_str: str = error.decode("utf-8")

        if error_str:
            logging.error("An error occurred during code execution: %s", error_str)
            return error_str
        else:
            logging.debug("Python code execution successful. Output: %s", output_str)
            return output_str

    except subprocess.TimeoutExpired:
        output_str = "Code execution timed out."
        logging.error("Code execution timed out.")
        return output_str

    except Exception as e:
        output_str = str(e)
        logging.error("An error occurred: %s", e)
        return output_str

    # try:
    #     # Initialize input string
    #     input_str = ""
    #
    #     # Hardcode test input values for testing
    #
    #
    #     # If input_values are provided and it's a list, convert them into a string to pass to stdin
    #     if input_values:
    #         if isinstance(input_values, list):
    #             input_str = '\n'.join(input_values)
    #         else:
    #             # Log an error if input_values is not a list
    #             logging.error("Input values must be a list.")
    #             # Handle the error scenario or raise an exception as appropriate
    #
    #     # Create a subprocess session
    #     with subprocess.Popen(['python', '-c', code], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE, text=True) as subprocess_session:
    #         # Write input to the subprocess stdin for each input value
    #         for input_value in input_values:
    #             subprocess_session.stdin.write(input_value + '\n')
    #
    #         subprocess_session.stdin.write('\n')  # Ensure there is an empty line to signal EOF
    #         subprocess_session.stdin.flush()
    #
    #         # Read output from the subprocess stdout
    #         output, error = subprocess_session.communicate()
    #
    #         # Combine stdout and stderr into output
    #         if error:
    #             output += "\nError:\n" + error
    #
    #         logging.debug("Python code execution successful. Output: %s", output)  # Log the output
    #
    #
    # except subprocess.TimeoutExpired:
    #     output = "Code execution timed out."
    #     logging.error("Code execution timed out.")
    #
    # except Exception as e:
    #     output = str(e)
    #     logging.error("An error occurred: %s", e)  # Log any other exceptions
    #
    # return output


@csrf_exempt
def lesson_process_code(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    tasks = Task.objects.filter(lesson_id=lesson.id)
    test_input_values = ["test_input_a", "test_input_b"]  # Define the test input values

    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                output = execute_python_code(code, test_input_values)  # Pass test_input_values to the function

                if "input(" in code:
                    prompt_message = code.split("input(")[1].split(")")[0].strip('"').strip("'")
                    return JsonResponse({'output': output, 'input_requested': True, 'prompt_message': prompt_message})
                else:
                    return JsonResponse({'output': output})
            except Exception as e:
                logging.error("An error occurred during code execution: %s", str(e))
                return JsonResponse({'error': 'An error occurred during code execution.'})
    else:
        form = CodeForm()

    return render(request, "courses/Show_lesson_process_page.html", {
        'form': form,
        'tasks': tasks,
        'lesson': lesson
    })


def content_process_form(request, content_id):
    course = get_object_or_404(Course, pk=content_id)
    lessons = Lesson.objects.filter(course_id=content_id)
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['prompts'] != "":
                additional_prompt: str = form.cleaned_data['prompts']
                # Combine original content response with additional prompt
                full_prompt = f"{course.response} {additional_prompt}"
                # Call OpenAI API with the full prompt and specified parameters
                processed_response = re_generate_content(full_prompt)
                if processed_response:
                    course.response = processed_response
                    course.prompts.append(additional_prompt)
                    course.save()
                return redirect('process_content', course.id)
    form = ContentForm()
    return render(request, 'courses/Show_content_process_form.html', {'form': form,
                                                                      'course': course,
                                                                      'lessons': lessons})


def validate_code(request, content_id):
    content = get_object_or_404(GeneratedContent, pk=content_id)
    if request.method == 'POST':
        form = GeneratedContentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['additional_prompt'] != "":
                additional_prompt = form.cleaned_data['additional_prompt']
                # Combine original content response with additional prompt
                full_prompt = f"{content.prompt} {additional_prompt}"

                # Call OpenAI API with the full prompt and specified parameters
                processed_response = generate_content(full_prompt)
                if processed_response:
                    content.response = processed_response
                    content.save()
                return redirect('process_code', content_id)
    else:
        form = GeneratedContentForm()

    return render(request, 'courses/process_code.html', {'form': form, 'content': content})


def display_content(request):
    # Fetch all the saved content from the database
    courses = Course.objects.all().order_by('-id')  # Newest first

    return render(request, 'courses/Show_generated_content.html', {'courses': courses})


def create_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            new_course_name = form.cleaned_data['title']
            number_lessons = form.cleaned_data['num_lessons']
            number_tasks = form.cleaned_data['num_tasks']
            objective = form.cleaned_data['objective']
            course_description: str = generate_description(objective)

            if not course_description:
                form.add_error(None, 'Failed to generate content.')
            else:
                new_course = Course.objects.create(title=new_course_name,
                                                   description=course_description,
                                                   objective=objective,
                                                   content=[])
                for i in range(number_lessons):
                    lesson_description = generate_structure(course_description, i, number_lessons)
                    lesson_title = generate_lesson_title(lesson_description)
                    new_lesson = Lesson.objects.create(course=new_course,
                                                       title=lesson_title,
                                                       description=lesson_description,
                                                       content=[])
                    new_course.content.append(new_lesson.title)
                    new_course.save()

                    for j in range(number_tasks):
                        task_content = generate_lesson_content(lesson_title, j)
                        if not task_content:
                            form.add_error(None, 'Failed to generate content.')
                        else:
                            new_task = Task.objects.create(lesson=new_lesson, title=task_content[1],
                                                           content=task_content[0])
                            new_lesson.content.append(new_task.title)
                            new_lesson.save()
                return redirect('display_content')  # Redirect to a new URL
    else:
        form = ContentForm()
    return render(request, 'courses/Show_content_generation_form.html', {'form': form})
# Create your views here.
