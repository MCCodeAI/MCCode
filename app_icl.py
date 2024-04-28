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

import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv()) 



#SendCode('')


 



@cl.on_chat_start
async def on_chat_start():
    
    llm = ChatOpenAI(name="MC Code", model_name="gpt-4-turbo", temperature=0, streaming=True)

    # Prompt for code generation
    prompt_template = '''
    I will give you some sample codes below, you need to follow the samples and make a python code step by step about {question}

Note: you need to do SetServoOn and homing for all the Axes mentioned in the question.
Sleep 0.1s between SetServoOn and homing.
Don't make up any functions, just follow the sample codes.
Print the result after each step.
    
 
"""<<<<<<<<<<<<<<<<<<<<<<<<<<<<PYTHON SAMPLE CODE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
This is a typical python code of WMX3 from initialization, through motion execution, to termination/closing/shutting down. The Python script initializes and operates a motion control system using the WMX3 software library, sequentially executing steps for robust control in an industrial setting. It starts by creating and naming a device with `CreateDevice('C:\\Program Files\\SoftServo\\WMX3\\', DeviceType.DeviceTypeNormal, INFINITE)` and `SetDeviceName('WMX3initTest')`, then begins communication with `StartCommunication(INFINITE)`. The script clears any amplifier alarms with `ClearAmpAlarm(axis)` and activates the servo with `SetServoOn(axis, 1)`. It executes a motion command using `StartMov(posCommand)` and concludes by shutting down the servo and stopping communication with `SetServoOn(axis, 0)` and `StopCommunication(INFINITE)`. This structured approach ensures each component is correctly set up and terminated, ensuring safe and effective system operations.
"""
 
 

#WMX3 python library
from WMX3ApiPython import *
from time import *


INFINITE = int(0xFFFFFFFF)


def main():
    Wmx3Lib = WMX3Api()
    CmStatus = CoreMotionStatus()
    Wmx3Lib_cm = CoreMotion(Wmx3Lib)
    ret = 0
    print('Program begin.')
    sleep(1)

    # Create devices.
    Wmx3Lib.CreateDevice('C:\\Program Files\\SoftServo\\WMX3', DeviceType.DeviceTypeNormal, INFINITE)

    # Set Device Name.
    Wmx3Lib.SetDeviceName('WMX3initTest')

    # Start Communication.
    ret = Wmx3Lib.StartCommunication(INFINITE)
    if ret!=0:
        print('start communicaiton fail!')
        return 0

    #Clear every servo/motor/amplifier's alarm
    timeoutCounter=0
    while True:
        # GetStatus -> First return value : Error code, Second return value: CoreMotionStatus
        ret, CmStatus = Wmx3Lib_cm.GetStatus()
        if (not CmStatus.GetAxesStatus(0).ampAlarm):
            break
        Wmx3Lib_cm.axisControl.ClearAmpAlarm(0)
        sleep(0.5)
        timeoutCounter=timeoutCounter+1
        if(timeoutCounter > 5):
            break
    if(timeoutCounter > 5):
        print('clear axis alarm fails!')
        return 0

    # Set servo on.
    Wmx3Lib_cm.axisControl.SetServoOn(0, 1)
    while True:
        # GetStatus -> First return value : Error code, Second return value: CoreMotionStatus
        ret, CmStatus = Wmx3Lib_cm.GetStatus()
        if (CmStatus.GetAxesStatus(0).servoOn):
            break
        sleep(0.1)

    #Sleep is a must between SetServoOn and Homing
    sleep(0.1) 
    # Homing
    homeParam = Config_HomeParam()
    ret, homeParam = Wmx3Lib_cm.config.GetHomeParam(0)
    homeParam.homeType = Config_HomeType.CurrentPos

    # SetHomeParam -> First return value: Error code, Second return value: param error
    ret, homeParamError = Wmx3Lib_cm.config.SetHomeParam(0, homeParam)

    Wmx3Lib_cm.home.StartHome(0)
    Wmx3Lib_cm.motion.Wait(0)

    # --------------------------------------------------------------------------
    # Create a command value.
    # --------------------------------------------------------------------------
    posCommand = Motion_PosCommand()
    posCommand.profile.type = ProfileType.Trapezoidal
    posCommand.axis = 0
    posCommand.target = 1000
    posCommand.profile.velocity = 1000
    posCommand.profile.acc = 1000000
    posCommand.profile.dec = 1000000

    # --------------------------------------------------------------------------
    # Execute command to move from current position to specified absolute position.
    # --------------------------------------------------------------------------
    Wmx3Lib_cm.motion.StartPos(posCommand)

    # --------------------------------------------------------------------------
    # Wait until the axis moves to the target position and stops.
    # --------------------------------------------------------------------------
    Wmx3Lib_cm.motion.Wait(0)

    # Set servo off.
    Wmx3Lib_cm.axisControl.SetServoOn(0, 0)
    while True:
        ret, CmStatus = Wmx3Lib_cm.GetStatus()
        if (not CmStatus.GetAxesStatus(0).servoOn):
            break
        sleep(0.1)

    # ----------------------
    # Stop Communication.
    # ----------------------
    Wmx3Lib.StopCommunication(INFINITE)

    # Close Device.
    Wmx3Lib.CloseDevice()

    print('Program End.')
    sleep(1)
    return 0


if __name__ == '__main__':
    main()




"""<<<<<<<<<<<<<<<<<<<<<<<<<<<<PYTHON SAMPLE CODE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
This is a typical python code of WMX3 for a axis/servo/motor to move or do positioning. 
"""

Wmx3Lib = WMX3Api()
CmStatus = CoreMotionStatus()
Wmx3Lib_cm = CoreMotion(Wmx3Lib)

# --------------------------------------------------------------------------
# Create a command value.
# --------------------------------------------------------------------------
posCommand = Motion_PosCommand()
posCommand.profile.type = ProfileType.Trapezoidal
posCommand.axis = 0
posCommand.target = 1000
posCommand.profile.velocity = 1000
posCommand.profile.acc = 1000000
posCommand.profile.dec = 1000000

# --------------------------------------------------------------------------
# Execute command to move to a specified absolute position. e.g. 'Move to Position 100..'
# --------------------------------------------------------------------------
Wmx3Lib_cm.motion.StartPos(posCommand)

# --------------------------------------------------------------------------
# Execute command to move from current position to a specified distance relatively. e.g. 'Move 100..'
# --------------------------------------------------------------------------
Wmx3Lib_cm.motion.StartMov(posCommand)


# --------------------------------------------------------------------------
# Wait until the axis moves to the target position and stops.
# --------------------------------------------------------------------------
Wmx3Lib_cm.motion.Wait(0)



"""<<<<<<<<<<<<<<<<<<<<<<<<<<<<PYTHON SAMPLE CODE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
This is a typical python code of WMX3 for a jog motion of a servo/motor/axis. 
"""
Wmx3Lib = WMX3Api()
CmStatus = CoreMotionStatus()
Wmx3Lib_cm = CoreMotion(Wmx3Lib)

jogCommand = Motion_JogCommand()
jogCommand.profile.type = ProfileType.Trapezoidal
jogCommand.axis = 0
jogCommand.profile.velocity = 1000
jogCommand.profile.acc = 100000
jogCommand.profile.dec = 100000

# Rotate the motor at the specified speed.
ret =Wmx3Lib_cm.motion.StartJog(jogCommand)
print(ret)

#Jogging for 3 seconds
sleep(3)
 
Wmx3Lib_cm.motion.Stop(0)



"""<<<<<<<<<<<<<<<<<<<<<<<<<<<<PYTHON SAMPLE CODE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
This is a typical python code of WMX3 to start an absolute position path interpolation motion command. This motion combines line interpolation and circular interpolation in one path, usually for continuous trajectory.
"""

Wmx3Lib = WMX3Api()
CmStatus = CoreMotionStatus()
Wmx3Lib_cm = CoreMotion(Wmx3Lib)
adv = AdvancedMotion(Wmx3Lib)
path = AdvMotion_PathIntplCommand()

path.SetAxis(0, 0)
path.SetAxis(1, 1)

path.enableConstProfile = 1

path.profile = Profile()
path.profile.type = ProfileType.Trapezoidal
path.profile.velocity = 1000
path.profile.acc = 100000
path.profile.dec = 100000

path.numPoints = 8

path.SetType(0, AdvMotion_PathIntplSegmentType.Linear)

path.SetTarget(0, 0, -200)
path.SetTarget(1, 0, -200)

path.SetType(1, AdvMotion_PathIntplSegmentType.Circular)
path.SetTarget(0, 1, -150)
path.SetTarget(1, 1, -200)
path.SetCenterPos(0, 1, 0)
path.SetCenterPos(1, 1, 0)
path.SetDirection(1, 1)

path.SetType(2, AdvMotion_PathIntplSegmentType.Linear)
path.SetTarget(0, 2, -180)
path.SetTarget(1, 2, -10)

path.SetType(3, AdvMotion_PathIntplSegmentType.Circular)
path.SetTarget(0, 3, -10)
path.SetTarget(1, 3, -150)
path.SetCenterPos(0, 3, 0)
path.SetCenterPos(1, 3, 0)
path.SetDirection(3, 1)

path.SetType(4, AdvMotion_PathIntplSegmentType.Linear)
path.SetTarget(0, 4, 0)
path.SetTarget(1, 4, -100)

path.SetType(5, AdvMotion_PathIntplSegmentType.Circular)
path.SetTarget(0, 5, -50)
path.SetTarget(1, 5, -100)
path.SetCenterPos(0, 5, 0)
path.SetCenterPos(1, 5, 0)
path.SetDirection(5, 1)

path.SetType(6, AdvMotion_PathIntplSegmentType.Linear)
path.SetTarget(0, 6, -50)
path.SetTarget(1, 6, 50)

path.SetType(7, AdvMotion_PathIntplSegmentType.Circular)
path.SetTarget(0, 7, 0)
path.SetTarget(1, 7, 0)
path.SetCenterPos(0, 7, 0)
path.SetCenterPos(1, 7, 0)
path.SetDirection(7, 1)

ret = adv.advMotion.StartPathIntplPos(path)
print(ret)
Wmx3Lib_cm.motion.Wait(0)

 
"""<<<<<<<<<<<<<<<<<<<<<<<<<<<<PYTHON SAMPLE CODE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
This is a typical python code of WMX3 IO to set an output bit to be 1, sleep for 1.8 seconds, and then set it to be 0.
"""
Wmx3Lib = WMX3Api()
CmStatus = CoreMotionStatus()
Wmx3Lib_cm = CoreMotion(Wmx3Lib)
Wmx3Lib_Io = Io(Wmx3Lib)
Wmx3Lib_Io.SetOutBit(0x0, 0x00, 0x01)
sleep(1.8)
Wmx3Lib_Io.SetOutBit(0x0, 0x00, 0x00)



"""<<<<<<<<<<<<<<<<<<<<<<<<<<<<PYTHON SAMPLE CODE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
This is a typical python code of WMX3 to start Start a absolute or relative position linear interpolation motion command.
"""
Wmx3Lib = WMX3Api()
CmStatus = CoreMotionStatus()
Wmx3Lib_cm = CoreMotion(Wmx3Lib)

lin = Motion_LinearIntplCommand()
lin.axisCount = 2 
lin.SetAxis(0,0)
lin.SetAxis(1,1) 

lin.profile.type = ProfileType.Trapezoidal
lin.profile.velocity = 1000
lin.profile.acc = 10000
lin.profile.dec = 10000

lin.SetTarget(0,30000)
lin.target(1,10000)

# Start an absolute position linear interpolation motion command.
ret =Wmx3Lib_cm.motion.StartLinearIntplPos(lin)
Wmx3Lib_cm.motion.Wait(0) #need to wait the Axis 0 to be idle
 
# Start an relative position linear interpolation motion command.
ret =Wmx3Lib_cm.motion.StartLinearIntplMov(lin)
Wmx3Lib_cm.motion.Wait(0) #need to wait the Axis 0 to be idle
    
    '''

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

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable


    msg = cl.Message(content="")
    
    # Task planning and retrieval pipeline.
    # completeTaskCode=await llm_pipeline(message.content)
    # questionMsg=completeTaskCode

    questionMsg=message.content

    async for chunk in runnable.astream(
        {"question": questionMsg},
        # {"context": format_docs(retriever.invoke(questionMsg)) , "question": questionMsg},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)
        # print(chunk)
    
 
    msgCode = extract_code(msg.content)
    print(msgCode)
    SendCode(msgCode)
    await msg.send()    
 

    print("end")


 