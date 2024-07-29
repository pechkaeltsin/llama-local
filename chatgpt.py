import json
import os
import time

import openai

client = openai.OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)


def get_value(obj):
    data = json.loads(obj.model_dump_json())
    value = data['data'][0]['content'][0]['text']['value']
    return value


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(0.5)
    return run


def ask(user_question):
    assistant_id = 'asst_KhT9oLcFudPb1TnM1Ab2TENj'

    assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_question
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    wait_on_run(run, thread)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="asc",
        after=message.id
    )

    return get_value(messages)


def delete_all_files():
    response = client.files.list(purpose="assistants")
    for file in response.data:
        client.files.delete(file.id)
    print("All files with purpose 'assistants' have been deleted.")


def add_file_to_vector_store(vector_store_id, file_ids):
    batch_add = client.beta.vector_stores.file_batches.create(
        vector_store_id=vector_store_id,
        file_ids=file_ids
    )
    time.sleep(1)
    print(batch_add.status)


def create_vector_store(name):
    vector_store = client.beta.vector_stores.create(
        name=name
    )
    return vector_store


def upload_files_to_vector_store(file_paths, vector_store_id):
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id,
        files=file_streams
    )

    print(file_batch.status)
    print(file_batch.file_counts)


def get_file_paths(directory='src/output'):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


