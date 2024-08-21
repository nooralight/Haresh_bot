from gpt_functions import create_assistant, updateAssistantInstruction, saveFile_intoOpenAI, create_vector_store, upload_file_into_vector_store, updateAssistantVectorDB


instruction = '''You are virtual representative of Padel Club. Users will ask you many FAQ questions. You will answer those questions from
your knowledge that you gained from data files.

## Special Instruction
1. If customer send message with other language rather than english, you will also send message with that language.
2. If there is any questions not related to Padel Club, you will nicely tell the customer that you don't have knowledge over this, and to try talking about the club.
3. Try to make shorter answer, within 1400 characters. The shorter answer, the better!'''

# print(updateAssistantInstruction("asst_aWNRkZ7hyEPkwjfHEgKtsMjr", instruction)) 
# print(saveFile_intoOpenAI("faq chatbot.docx"))

create_assistant("haresh", instruction)

# print(create_vector_store("haresh_faq"))
# upload_file_into_vector_store("vs_5ADy3AEuORnW0qcuN53WNnJF", ['file-Ex1tK7pDPGQuR6zltRrschdz'])
# updateAssistantVectorDB("asst_aWNRkZ7hyEPkwjfHEgKtsMjr","vs_5ADy3AEuORnW0qcuN53WNnJF")