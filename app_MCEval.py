from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader, TextLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings, OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage

import chainlit as cl
import time
from CodeClient import *
from make_code_runnable import *
from plot_log import *

import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv()) 

#SendCode('')

# Vectorstore 
embedding_model=OpenAIEmbeddings(model="text-embedding-3-large")   #text-embedding-3-large   #text-embedding-ada-002    #text-embedding-3-small

# If pdf vectorstore exists
vectorstore_path = "Vectorstore/chromadb-MCCoder"
if os.path.exists(vectorstore_path):
    vectorstore = Chroma(
                    embedding_function=embedding_model,
                    persist_directory=vectorstore_path,
                    ) 
    print("load from disk: " + vectorstore_path)
else:
        # Load from chunks and save to disk
    # vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model, persist_directory=vectorstore_path) 
    print("load from chunks")

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Global variable to store the name of the LLM
llm_name = None

@cl.on_chat_start
async def on_chat_start():
    
    llm = ChatOpenAI(name="MCCoder and QA", model_name="gpt-4o", temperature=0.2, streaming=True)

    global llm_name
    # Store the name of the LLM in the global variable
    llm_name = llm.model_name

    # Prompt for code generation
    prompt_template = """Write a python code based on the following Question and Context. 
    1. Review the question carefully and find all the 'Axis number', and add them to the first line of the generated code in the following format: 
    # Axes = ['Axis number 1', 'Axis number 2', ...].
    For instance, if the question is '...Axis 9..., ...Axis 12..., ...Axis 2...', then '# Axes = [9, 12, 2]'.
    2. Include all the generated codes within one paragraph between ```python and ``` tags. 
    3. Don't import any library you don't know.

    Question: {question}

    Context: {context}

        """

    prompt_code = ChatPromptTemplate.from_template(prompt_template)

    runnable = (
        # {"context": retriever | format_docs}
         prompt_code
        | llm
        | StrOutputParser()
    )

    cl.user_session.set("runnable", runnable)


@cl.step
async def agentTaskPlanner(inputMsg):
   
    llmTask = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    template = """You are recognized for your exceptional skill in task decomposition. Your objective is to break down the presented question (task) into precise and clear sub-tasks, each numbered sequentially, without adding explanations.

        For queries framed as a singular, straightforward sentence, your responses should naturally incorporate the initiation and closing of WMX as part of the process. An illustration of this approach is as follows:

        Question: "Write a code to move Axis 1 to position 1000."
        Sub-tasks:

        1. Initialize WMX
        2. Move Axis 1 to position 1000
        3. Close WMX

        In situations where the query encompasses multiple directives within a few sentences, decompose the question into separate, ordered sub-tasks. A sample for this scenario is given below:

        Question: "Write a code to initialize WMX, move Axis 1 to position 1000, sleep for 2 seconds, set output 3.4 to 1, and subsequently close WMX."
        Sub-tasks:

        1. Initialize WMX
        2. Move Axis 1 to position 1000
        3. Sleep for 2 seconds
        4. Set output 3.4 to 1
        5. Close WMX

        Question: {question}

        Sub-tasks:
        """

    custom_rag_prompt = PromptTemplate.from_template(template)
    
    rag_chain = (
            {"question": RunnablePassthrough()}
            | custom_rag_prompt
            | llmTask
            | StrOutputParser()
        )

    MTask=rag_chain.invoke(inputMsg)

    return(MTask)


llmsubTask = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)


@cl.step
async def agentSubTaskCode(subTask):
   # remember to write "python" code in the prompt later
    template = """You are an expert in motion control in WMX3 which is a software controller. You can answer the question based on the context, and give a concise code to invoke WMX3 apis, with code comments. 

        {context}

        Question: "write a c++ code: " + {question}

        Answer:
        """

    custom_rag_prompt = PromptTemplate.from_template(template)
    
    rag_chain = (
            {"context": retriever | format_docs, "question": 
        RunnablePassthrough()}
            | custom_rag_prompt
            | llmsubTask
            | StrOutputParser()
        )

    subTaskCode=rag_chain.invoke(subTask)
 
    return(subTaskCode)

llmSelector = ChatOpenAI(model_name="gpt-4o", temperature=0)

@cl.step
async def MCClassifier(userquestion):
   # remember to write "python" code in the prompt later
    template = '''You are a selector to choose which agent to go based on the {userquestion}.

        1. If it is about python code and there are not Initializing and Closing WMX3 in it, then output:
        "Write a python code to Initialize WMX3, and {userquestion}, and Close WMX3."

        2. If it is a general question, then output:
        {userquestion}

        Output:
        '''

    custom_rag_prompt = PromptTemplate.from_template(template)
    
    rag_chain = (
            {"userquestion": RunnablePassthrough()}
            | custom_rag_prompt
            | llmSelector
            | StrOutputParser()
        )

    SelectorOutput=rag_chain.invoke(userquestion)
 
    return(SelectorOutput)



def format_docs(docs):
   return "\n\n".join(doc.page_content for doc in docs)

@cl.step
async def llm_pipeline(inputMsg):

    MTask = await agentTaskPlanner(inputMsg)
    
    completeTaskCode = ""
    subTasks = MTask.split('\n')
    subTaskCount = 0
    for subTask in subTasks:
        if subTask == "": continue
        subTaskCount += 1
        # if subTaskCount == 2: continue
        
        subTaskCode = await agentSubTaskCode(subTask)
    
        completeTaskCode += "\n" + str(subTaskCount) + ".\n" +subTaskCode

    return(completeTaskCode)
 
import re
def extract_code(text):
    # Define the regular expression pattern to find text between ```python and ```
    pattern = r"```python(.*?)```"

    # Use re.findall to find all occurrences
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the matches, join them if there are multiple matches
    return "\n\n---\n\n".join(matches)


@cl.step
# Extracts and formats code instructions from a user question based on specific starting phrases.
async def coder_router(user_question):
    """
    Extracts numbered sections of a user question based on specific starting phrases.
    
    If the question starts with 'Write a python code', 'Python code', or 'write python' (case insensitive),
    it splits the question into paragraphs that start with numbers (e.g., 1., 2., 3.) and adds 
    'Write python code to ' after the numbers. If the question does not start 
    with the specified phrases or does not contain numbered lists, the entire question is saved into a single 
    element array. If the question does not start with the specified phrases, NoCoder is set to 1.
    
    Args:
        user_question (str): The user's question.
    
    Returns:
        tuple: NoCoder (int), an array of strings with each element containing a code instruction or the entire question.
    """
    result = []
    NoCoder = 0
    # Check if the input starts with the specified prefixes
    if re.match(r'(?i)^(Write a python code|Python code|write python)', user_question):
        result.append(user_question)
    else:
        # Save the entire question to the array and set NoCoder to 1
        result.append(user_question)
        NoCoder = 1
    
    return NoCoder, result


@cl.step
# This function retrieves and concatenates documents for each element in the input string array.
async def coder_retrieval(coder_router_result):
    """
    This function takes an array of strings as input. For each element in the array,
    it performs a retrieval using format_docs(retriever.invoke(element))
    and concatenates the element with the retrieval result into one long string, 
    with a newline character between them. Each concatenated result is separated by a specified separator.
    
    Args:
        coder_router_result (list): An array of strings.

    Returns:
        str: A single long string formed by concatenating each element with its retrieval result,
             separated by a newline character, and each concatenated result separated by a specified separator.
    """
    separator = "\n----------\n"
    long_string = ""
    for element in coder_router_result:
        retrieval_result = format_docs(retriever.invoke(element))
        long_string += element + "\n" + retrieval_result + separator
    
    return long_string



@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")
    
    # Task planning and retrieval pipeline.
    # completeTaskCode=await llm_pipeline(message.content)
    # questionMsg=completeTaskCode

    # Question for agent selection.
    # QuestionSeletorOutput=await MCClassifier(message.content)
    # questionMsg=QuestionSeletorOutput

    # Input text
    user_question = message.content
    
    # Call coder_router function
    NoCoder, coder_router_result = await coder_router(user_question)
    
    # Route the result based on NoCoder value
    if NoCoder == 0:
        coder_return = await coder_retrieval(coder_router_result)
        context_msg = coder_return
    else:
        context_msg = format_docs(retriever.invoke(coder_router_result[0]))

    # questionMsg=message.content


    async for chunk in runnable.astream(
        # {"question": questionMsg},
        {"context": context_msg, "question": user_question},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)
        # print(chunk)

    task_info = "0"
    # Get python code from the output of LLM
    msgCode = extract_code(msg.content)
    RunnableCode = make_code_runnable(msgCode, llm_name, task_info)
    print(RunnableCode)

    SendCode(RunnableCode)
    
    folder_path = r'/Users/yin/Documents/GitHub/MCCodeLog'
    os.makedirs(folder_path, exist_ok=True)

    log_file_path = os.path.join(folder_path, f"{task_info}_{llm_name}_log.txt")
    plot_log(log_file_path)
    
    # 定义文件名
    plot_filenames = [
        f"{task_info}_{llm_name}_log_plot.png",
        f"{task_info}_{llm_name}_log_2d_plot.png",
        f"{task_info}_{llm_name}_log_3d_plot.png"
    ]
    
    for filename in plot_filenames:
        file_path = os.path.join(folder_path, filename)
        if os.path.exists(file_path):
            image = cl.Image(path=file_path, name=filename, display="inline", size='large')
            # Attach the image to the message
            await cl.Message(
                content=f"Plot name: {filename}",
                elements=[image],
            ).send()
            
    text_content = "Hello, this is a text element."
    
    apitext = [
        cl.Text(name="simple_text", content=text_content)
    ]

    await cl.Message(
        content="API reference:",
        elements=apitext,
    ).send()

    await msg.send()    

    print("end")


 