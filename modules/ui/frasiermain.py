import time
import os
import simplejson as json
import re
import traceback
from termcolor import colored

from frasier.common.AConfig import config
from frasier.core.AProcessor import AProcessor
from frasier.core.llm.ALLMPool import ALLMPool
from frasier.common.utils.ALogger import ALogger
from frasier.common.ARemoteAccessors import AClientPool
from frasier.common.AMessenger import AMessenger
from frasier.AServices import StartServices, TerminateSubprocess

from frasier.common.APrompts import APromptsManager
from frasier.prompts.APromptChat import APromptChat
from frasier.prompts.APromptMain import APromptMain
from frasier.prompts.APromptSearchEngine import APromptSearchEngine
from frasier.prompts.APromptResearcher import APromptResearcher
from frasier.prompts.APromptCoder import APromptCoder
from frasier.prompts.APromptModuleCoder import APromptModuleCoder
from frasier.prompts.APromptCoderProxy import APromptCoderProxy
from frasier.prompts.APromptArticleDigest import APromptArticleDigest


def GetInput(speech) -> str:
    if config.speechOn:
        print(colored("USER: ", "green"), end="", flush=True)
        inp = speech.GetAudio()
        print(inp, end="", flush=True)
        print("")
    else:
        inp = input(colored("USER: ", "green"))
    return inp

def mainLoop(session: str):
    print(colored("In order to simplify installation and usage, we have set local execution as the default behavior, which means AI has complete control over the local environment. \
To prevent irreversible losses due to potential AI errors, you may consider one of the following two methods: the first one, run frasier in a virtual machine; the second one, install Docker, \
use the provided Dockerfile to build an image and container, and modify the relevant configurations in config.json. For detailed instructions, please refer to the documentation.", "red"))

    print(colored("If you find that frasier is running slowly or experiencing high CPU usage, please run `frasier_turbo` to install GPU acceleration support.", "green"))
    
    if "" != session.strip():
        sessionPath = os.path.join(config.chatHistoryPath, session)
        storagePath = os.path.join(sessionPath, "storage")
        historyPath = os.path.join(sessionPath, "frasier_history.json")
        os.makedirs(sessionPath, exist_ok=True)
        os.makedirs(storagePath, exist_ok=True)
    else:
        storagePath = ""
    
    clientPool = AClientPool()
    StartServices()
    for i in range(5):
        try:
            clientPool.Init()
            break
        except Exception as e:
            if i == 4:
                print(f"It seems that some peripheral module services failed to start. EXCEPTION: {str(e)}")
                print(e.tb) if hasattr(e, 'tb') else traceback.print_tb(e.__traceback__)
                exit(-1)
            time.sleep(5)
            continue
    
    print(colored(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", "green"))
    print("We now start the vector database. Note that this may include downloading the model weights, so it may take some time.")
    storage = clientPool.GetClient(config.services['storage']['addr'])
    msg = storage.Open(storagePath)
    print(f"Vector database has been started. returned msg: {msg}")
    print(colored(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", "green"))

    if config.speechOn:
        speech = clientPool.GetClient(config.services['speech']['addr'])
        print(colored(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", "green"))
        print("The speech module is preparing speech recognition and TTS models, which may include the work of downloading weight data, so it may take a long time.")
        speech.PrepareModel()
        print("The speech module model preparation work is completed.")
        print(colored(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", "green"))
        if any([re.fullmatch(r"(cuda|cpu)(:(\d+))?", s) == None for s in [config.ttsDevice, config.sttDevice]]):
            print("the value of ttsDevice and sttDevice should be a valid cuda device, such as cuda, cuda:0, or cpu, the default is cpu.")
            exit(-1)
        else:
            speech.SetDevices({"tts": config.ttsDevice, "stt": config.sttDevice})
    else:
        speech = None
    
    timestamp = str(int(time.time()))
    collection = "frasier_" + timestamp

    promptsManager = APromptsManager()
    promptsManager.Init(storage=storage, collection=collection)
    promptsManager.RegisterPrompts([APromptChat, APromptMain, APromptSearchEngine, APromptResearcher, APromptCoder, APromptModuleCoder, APromptCoderProxy, APromptArticleDigest])
    
    llmPool = ALLMPool()
    llmPool.Init([config.modelID])
    
    logger = ALogger(speech=speech)
    processor = AProcessor(name='frasier', modelID=config.modelID, promptName=config.prompt, llmPool=llmPool, promptsManager=promptsManager, services=clientPool, messenger=AMessenger(), outputCB=logger.Receiver, collection=collection)
    processor.RegisterModules([config.services['browser']['addr'],
                               config.services['arxiv']['addr'],
                               config.services['google']['addr'],
                               config.services['duckduckgo']['addr'],
                               config.services['scripter']['addr'],
                               config.services['computer']['addr']] + ([config.services['speech']['addr']] if config.speechOn else []))

    if "" != session.strip():
        if os.path.exists(historyPath):
            with open(historyPath, "r") as f:
                processor.FromJson(json.load(f))
    
    while True:
        if "" != session.strip():
            with open(historyPath, "w") as f:
                    json.dump(processor.ToJson(), f, indent=2)
        inpt = GetInput(speech)
        processor(inpt)
    return

def main():
    config.Initialize()
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--modelID',type=str,default=config.modelID, help="modelID specifies the model. There are two modes for model configuration. In the first mode, the model is uniformly specified by modelID. In the second mode, different types of agents will run on different models. When this parameter is an empty string (unspecified), the second mode will be used automatically, i.e., the models configured individually for different agents under the agentModelConfig field in config.json will be used. The currently supported models can be seen in config.json. Default: %(default)s")
    parser.add_argument('--quantization',type=str,default=config.quantization, help="quantization is the quantization option, you can choose 4bit or 8bit. Default: %(default)s")
    parser.add_argument('--maxMemory',type=dict,default=config.maxMemory, help='maxMemory is the memory video memory capacity constraint, the format when set is like "{0:"23GiB", 1:"24GiB", "cpu": "64GiB"}". Default: %(default)s')
    parser.add_argument('--prompt',type=str,default=config.prompt, help="prompt specifies the prompt to be executed, which is the type of agent. Default: %(default)s")
    parser.add_argument('--temperature',type=float,default=config.temperature, help="temperature sets the temperature parameter of LLM reasoning. Default: %(default)s")
    parser.add_argument('--flashAttention2',type=bool,default=config.flashAttention2, help="flashAttention2 is the switch to enable flash attention 2 to speed up inference. It may have a certain impact on output quality. Default: %(default)s")
    parser.add_argument('--contextWindowRatio',type=float,default=config.contextWindowRatio, help="contextWindowRatio is a user-specified proportion coefficient, which determines the proportion of the upper limit of the prompt length constructed during inference to the LLM context window in some cases. Default: %(default)s")
    parser.add_argument('--speechOn',type=bool,default=config.speechOn, help="speechOn is the switch to enable voice conversation. Please note that the voice dialogue is currently not smooth yet. Default: %(default)s")
    parser.add_argument('--ttsDevice',type=str,default=config.ttsDevice,help='ttsDevice specifies the computing device used by the text-to-speech model. You can set it to "cuda" if there is enough video memory. Default: %(default)s')
    parser.add_argument('--sttDevice',type=str,default=config.sttDevice,help='sttDevice specifies the computing device used by the speech-to-text model. You can set it to "cuda" if there is enough video memory. Default: %(default)s')
    parser.add_argument('--chatHistoryPath',type=str,default=config.chatHistoryPath, help="chatHistoryPath is used to specify the chat history storage path. Default: %(default)s")
    parser.add_argument('--session',type=str,default='', help="session is used to specify the session storage path, if the directory is not empty, the conversation history stored in that directory will be loaded and updated. Default: %(default)s")
    kwargs = vars(parser.parse_args())

    config.Check4Update(kwargs['modelID'])
    config.Update(kwargs)
    
    try:
        mainLoop(session = kwargs['session'])
    except Exception as e:
        print(f"Encountered an exception, frasier is exiting: {str(e)}")
        print(e.tb) if hasattr(e, 'tb') else traceback.print_tb(e.__traceback__)
        TerminateSubprocess()
        raise

if __name__ == '__main__':
    main()
