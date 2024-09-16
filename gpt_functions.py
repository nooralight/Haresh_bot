from openai import OpenAI
import function_tools as ft
import os
from dotenv import load_dotenv
load_dotenv()
# Configure OpenAI API key from environment variable
openAI_key = os.getenv('OPENAI_KEY')

## Function to upload file into OpenAI
def saveFile_intoOpenAI(file_location):
    client = OpenAI(api_key=openAI_key)
    file = client.files.create(
        file=open(file_location, "rb"),
        purpose='assistants'
    )
    return file.id

# Delete file from openai
def deleteFile(file_id):
    client = OpenAI(api_key=openAI_key)
    file_deletion_status = client.files.delete(file_id = file_id)

    return file_deletion_status


# Creating assistant
def create_assistant(assistant_name, my_instruction):
    client = OpenAI(api_key=openAI_key)
    my_assistant = client.beta.assistants.create(
        name = assistant_name,
        instructions = my_instruction,
        description = "A human like representative of Haresh Padel Club",
        model="gpt-4o",
        tools=[{"type": "file_search"}, ft.see_available_padels, ft.make_padel_event, ft.show_padel_event],
	)
    
    return my_assistant.id

def show_assistants():
    client = OpenAI(api_key=openAI_key)
    my_updated_assistant = client.beta.assistants.list()
    return my_updated_assistant

def updateAssistantInstruction(assistant_id,new_instruction):
    client = OpenAI(api_key=openAI_key)
    my_updated_assistant = client.beta.assistants.update(assistant_id,instructions=new_instruction)
    return my_updated_assistant

def updateAssistantVectorDB(assistant_id, vector_store_id):
    client = OpenAI(api_key=openAI_key)
    assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )


# Create a vector store 
def create_vector_store(store_name):
    client = OpenAI(api_key=openAI_key)
    vector_store = client.beta.vector_stores.create(name=store_name)
    return vector_store.id


# upload file into a vector store 
def upload_file_into_vector_store(vector_store_id ,file_ids):
    client = OpenAI(api_key=openAI_key)
 
    file_batch = client.beta.vector_stores.file_batches.create(
        vector_store_id=vector_store_id, file_ids=file_ids
    )
 
    # Print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)

    print("Done Uploading")


def delete_vector_store_file(vector_store_id, file_id):
    client = OpenAI(api_key=openAI_key)

    deleted_vector_store_file = client.beta.vector_stores.files.delete(
        vector_store_id=vector_store_id,
        file_id=file_id
    )
    print(deleted_vector_store_file)


## Create the Thread
def createThread(prompt):
    client = OpenAI(api_key=openAI_key)
    messages = [{"role":"user", "content": prompt}]
    thread = client.beta.threads.create(messages = messages)
    return thread.id


## Run the Assitance
def runAssistant(thread_id, asssitant_id):
    client = OpenAI(api_key=openAI_key)
    run = client.beta.threads.runs.create(thread_id = thread_id, assistant_id = asssitant_id)
    return run

# ## See run status
# def checkRunStatus(thread_id, run_id):
#     client = OpenAI(api_key=openAI_key)
#     run = client.beta.threads.runs.retrieve(thread_id = thread_id, run_id = run_id)
#     return run

# ## Retrieve Response from the thread
# def retrieveResponse(thread_id):
#     client = OpenAI(api_key=openAI_key)
#     thread_messages = client.beta.threads.messages.list(thread_id)
#     list_messages = thread_messages.data
#     assistant_message = list_messages[0]
#     #reference = assistant_message.content[0].text.annotations[0].file_citation.quote
#     message_text = assistant_message.content[0].text.value
#     return message_text

## Send New Message to the thread

def sendNewMessage(thread_id,prompt):
    client = OpenAI(api_key=openAI_key)
    thread_message = client.beta.threads.messages.create(thread_id, role= "user", content = prompt)


# Create thread
def initiate_interaction(user_message):
    client = OpenAI(api_key=openAI_key)
    my_thread = client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": "Write and answer to the question- "+user_message
            }
        ]
    )
    return my_thread.id


# sending message to existing thread
def sendNewMessage_to_existing_thread(thread_id,message):
    client = OpenAI(api_key=openAI_key)
    thread_message = client.beta.threads.messages.create(thread_id, role= "user", content = message)


# starting a thread
def trigger_assistant(my_thread_id, my_assistant):
    client = OpenAI(api_key=openAI_key)
    run = client.beta.threads.runs.create(thread_id = my_thread_id, assistant_id = my_assistant)
    return run


## See run status
def checkRunStatus(thread_id, run_id):
    client = OpenAI(api_key=openAI_key)
    run = client.beta.threads.runs.retrieve(thread_id = thread_id, run_id = run_id)
    return run

## Retrieve Response from the thread
def retrieveResponse(thread_id):
    client = OpenAI(api_key=openAI_key)
    thread_messages = client.beta.threads.messages.list(thread_id)
    list_messages = thread_messages.data
    assistant_message = list_messages[0]
    message_text = assistant_message.content[0].text.value
    return message_text

# vector_store_id = create_vector_store(["output.txt"])
# updateAssistantVectorDB(MY_ASSISTANT_ID, vector_store_id)


# instruction="""Your name is Alfred. You are a polite and highly skilled medical professional with profound knowledge in Medical information. But you know nothing outside medical domain.
# You have been employed by a Hospital named Labaid Hospitals Ltd. and your task is to answer questions to customers' queries regarding medical issues and provide solutions. 
# If a solution is provided by the hospital, you will mention it to the customer that you can do this to get healthy 
# and we also provide this service that might help you get better.
# The company ordered you not to answer irrelevant questions that doesn't go with medical queries or hospital related queries.

# ## Welcome message
# Always start conversation with proper greeting mentioning your name.
# For example- "Hello, Alfred here at your service. How can I help you?"

# ## Special Instruction
# 1. Make sure that you never mention your shortcomings like my knowledge is limited to this certain data or this time limit. 
# For example- don't say 'my knowledge is limited to 2023' or 'I can only answers withing 2023 domain'.
# 2. Responses must not exceed 1600 characters.
# 3. Make sure to mention your name whie greeting or starting the conversation.
# 4. If customer send you unrelated messages or questions which are not related to Medical information, simply send a message "Please send messages to us related to medical information. Thank you!"
# """ 

# print(create_assistant("Alfred_final", instruction))
# updateAssistantVectorDB("asst_iijGEc4KlIqrVZ9mLVhZdZbe", "vs_joHKCuQfUT45GKH1ppZtqK7y")

# instruction = '''You are Nick Regan, a Leadership Coach / Experienced Team Coach / Dialogue Facilitator, who shares strategies and tools for leaders. Your key focus area is all the knowledge that is uploaded in this chatbot.

# Users of this chatbot will ask you questions. Your task is to provide answers to the user question ONLY IF YOU CAN ANSWER WITH THE KNOWLEDGE FROM THE DOCUMENTS, give the user guidance, tips, and advice on these topics, and answer any question that the user has if the answer can be find in the documents.

# The way you respond will be in the exact style that Nick Regan would respond. Deeply analyze how Nick Regan writes, find patterns in his writing style and copy this exact style to mimic his writing, this way it will be just as if Nick Regan is responding to the input. 

# Always answer the query directly in as few words as possible, make it a simple short answer that is practicle, informational and usefull for the user. Only provide long-form answers if the user has specifically asked for a plan, guide, or other type of output that requires a lot of text.

# Assess the provided document to decide if it's useful/relevant to the question. If not, so if you can't answer the question with the knowledge, then always respond with "I apologise but the answer to this question is outside of the knowledge available on my chatbot. 
# Please feel free to connect with me via linkedin or email if you'd like to connect and explore the 
# question together.". Use only the information provided in the documents! Only send this message if you cant answer the input with the knowledge of the documents. Do not use your general knowledge to generate new or expanded topics. You can only respond with the knowledge in the documents, if you can't answer then send my provided message.

# NEVER mention the context snippets you're provided with. It should seem like you already possess this information and are merely sharing your knowledge as Nick Regan himself. NEVER make references to yourself in the third person; ALWAYS speak in the first person.

# You are in an ongoing conversation with the user, do not end your responses with "good luck with __!" or "let me know if I can help with anything else!". DO NOT finish messages with these kinds of endings.

# You will also be provided with the recent chat history as context. Create your responses to be aware of the recent messages but always focus primarily on the most recent message, then second most recent and so on in creating your responses

# ## Special Instruction:

# 1. If someone ask you unnecessary questions or questions that are not in your interest based on the instruction I give you, tell them nicely "I apologise but the answer to this question is outside of the knowledge available on my chatbot. 
# Please feel free to connect with me via linkedin or email if you'd like to connect and explore the  question together.'''

# print(updateAssistantInstruction("asst_0JoLPz3GaN0L1HtgedTsf3Yn", instruction)) 

# print(show_assistants())