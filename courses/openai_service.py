import openai
import json
from openai import OpenAI
import time
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))


def check_run(client, thread_id, run_id):
    while True:
        # Refresh the run object to get the latest status
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run.status == "completed":
            return "completed"
            break
        elif run.status == "expired":
            return "expired"
            break
        else:
            time.sleep(5)  # Wait for 1 second before checking again


# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def message_loop(prompt, assistant_id, thread_id):
    print('check if loop started')
    while True:
        # Convert prompt to string if it's a list
        if isinstance(prompt, list):
            prompt_str = ' '.join(prompt)
        else:
            prompt_str = str(prompt)

        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt_str
        )
        print("message: ", message)
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        print("run_1: ", run)
        if check_run(client, thread_id, run.id) == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            assistant_message = messages.data[0].content[0].text.value
            return assistant_message
            break


def assistant_preprocess_task(code, output, thread_id, task_description):
    print('check if assistant started')
    try:
        prompt_1 = 'There is a task: ' + str(task_description)
        prompt_2 = "In following code please check every line and validate execution response. Advise if code does not correspond to the task: \
                         \n" + code + '\nExecution response:\n' + str(output) + '\nShow corrected code in the end, but only if \
                         corrected code really change the result of code execution. Return message <<Code is ok!>> if code correctly address the task.'
        request = f"{prompt_1}{prompt_2}"
        assistant_id = 'asst_Kx2zKp0x0r3fLA6ZFiIGVsPZ'
        ai_response = message_loop(request, assistant_id, thread_id)

        return ai_response, assistant_id, thread_id
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


def assistant_thread_run(code, thread_id, output=None):
    print(thread_id)
    try:
        prompt = "In following code please check every line and validate execution response. Advise code corrections if any issue is detected: \
                 \n" + code + '\nExecution response:\n' + str(output) + '\nShow corrected code in the end, but only if \
                 corrected code really change the result of code execution. Provide short answer: <<Code is ok!>>'
        assistant_id = 'asst_Kx2zKp0x0r3fLA6ZFiIGVsPZ'
        ai_response = message_loop(prompt, assistant_id, thread_id)

        return ai_response, assistant_id, thread_id
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


def generate_description(prompt):
    generic_prompt_1 = "Please generate learning program description, for the course objective:"
    generic_prompt_2 = ". Limit answer to maximum 500 symbols"
    request = f"{generic_prompt_1} {prompt} {generic_prompt_2} "
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": request,
                },
            ],
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


def generate_structure(description, i, n):
    generic_prompt_1 = "For the following learning course: "
    generic_prompt_2 = "generate maximum 100 word description of the lesson number"
    generic_prompt_3 = "out of "
    try:
        request = f"{generic_prompt_1} {description} {generic_prompt_2} {i} {generic_prompt_3} {n}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "assistant",
                    "content": request,
                },
            ],
        )
        response_text = response.choices[0].message.content.strip()
        return response_text
    except Exception as e:
        print(f"Error generating content for: {e}")
        return None


def generate_lesson_title(lesson):
    generic_prompt = "Please generate lesson title for the following lesson description:"
    request = f"{generic_prompt} {lesson}"
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "assistant",
                    "content": request,
                },
            ],
        )

        title = response.choices[0].message.content
        print("title:", title)
        return title
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


def generate_project_content(desc):
        generic_prompt_1 = "Please generate Project Task example of correct code snippet with #comments for the topics listed\n"
        generic_prompt_2 = "Please formulate Project assignment based on the solution code for it:\n"
        request_1 = f"{generic_prompt_1} {desc}"

        try:
            response_1 = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "assistant",
                        "content": request_1,
                    },
                ],
            )
            request_2 = f"{generic_prompt_2} {response_1}"
            response_2 = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "assistant",
                        "content": request_2,
                    },
                ],
            )
            project_solution = response_1.choices[0].message.content
            project_question = response_2.choices[0].message.content
            # Splitting the response into parts based on newline
            # task_lines = response_text.splitlines()

            return project_solution, project_question
        except Exception as e:
            print(f"Error generating content: {e}")
            return None


def generate_lesson_content(title):
    generic_prompt_1 = "Please generate example of correct code snippet with #comments for the topic description below\n"
    generic_prompt_2 = "Please formulate exercise question based on the solution code for it:\n"
    request_1 = f"{generic_prompt_1} {title}"

    try:
        response_1 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "assistant",
                    "content": request_1,
                },
            ],
        )
        request_2 = f"{generic_prompt_2} {response_1}"
        response_2 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "assistant",
                    "content": request_2,
                },
            ],
        )
        task_solution = response_1.choices[0].message.content
        task_question = response_2.choices[0].message.content
        # Splitting the response into parts based on newline
        # task_lines = response_text.splitlines()

        return task_question, task_solution
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


def re_generate_content(prompt):
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error generating content: {e}")
        return None
