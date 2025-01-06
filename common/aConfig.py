import os
import sys
import json
import appdirs
import requests
from termcolor import colored

class AConfig():
    def __init__(self):
        self.modelID = ""
        self.agentModelConfig = {"DEFAULT": "openrouter:qwen/qwen-2.5-72b-instruct",
                                 "main": "openrouter:anthropic/claude-3.5-sonnet",
                                 "coder": "openrouter:qwen/qwen-2.5-coder-32b-instruct"}
        self.prompt = "main"
        self.chatHistoryPath = appdirs.user_data_dir("frasier", "Steven Lu")
        self.certificate = ""
        self.maxMemory = {}
        self.quantization = None
        self.models = {
            "hf": {
                "modelWrapper": "AModelCausalLM",
                "modelList": {
                    "meta-llama/Llama-2-13b-chat-hf": {"formatter": "AFormatterLLAMA2", "contextWindow": 4096, "systemAsUser": False, "args": {}},
                    "meta-llama/Llama-2-70b-chat-hf": {"formatter": "AFormatterLLAMA2", "contextWindow": 4096, "systemAsUser": False, "args": {}},
                    "meta-llama/Meta-Llama-3-8B-Instruct": {"formatter": "AFormatterLLAMA3", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "meta-llama/Meta-Llama-3-70B-Instruct": {"formatter": "AFormatterLLAMA3", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "Phind/Phind-CodeLlama-34B-v2": {"formatter": "AFormatterSimple", "contextWindow": 4096, "systemAsUser": False, "args": {}},
                    "mistralai/Mistral-7B-Instruct-v0.1": {"formatter": "AFormatterLLAMA2", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "Open-Orca/Mistral-7B-OpenOrca": {"formatter": "AFormatterChatML", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "teknium/OpenHermes-2.5-Mistral-7B": {"formatter": "AFormatterChatML", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "mistralai/Mixtral-8x7B-Instruct-v0.1": {"formatter": "AFormatterSimple", "contextWindow": 32000, "systemAsUser": False, "args": {}},
                    "ehartford/dolphin-2.5-mixtral-8x7b": {"formatter": "AFormatterChatML", "contextWindow": 16000, "systemAsUser": False, "args": {}},
                    "openchat/openchat_3.5": {"formatter": "AFormatterOpenChat", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO": {"formatter": "AFormatterChatML", "contextWindow": 32000, "systemAsUser": False, "args": {}},
                    "CohereForAI/c4ai-command-r-plus-4bit": {"formatter": "AFormatterCommandR", "contextWindow": 128000, "systemAsUser": False, "args": {}},
                },
            },
            "peft": {
                "modelWrapper": "AModelCausalLM",
                "modelList": {
                    #"model/": {"formatter": "AFormatterChatML", "contextWindow": 8192, "systemAsUser": False, "args": {}}
                }
            },
            "oai": {
                "modelWrapper": "AModelChatGPT",
                "apikey": None,
                "baseURL": None,
                "modelList": {
                    "o1-preview": {"formatter": "AFormatterGPT", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "o1-preview-2024-09-12": {"formatter": "AFormatterGPT", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "o1-mini": {"formatter": "AFormatterGPT", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "o1-mini-2024-09-12": {"formatter": "AFormatterGPT", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "gpt-4o": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "gpt-4o-2024-05-13": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "gpt-4o-2024-08-06": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "chatgpt-4o-latest": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "gpt-4o-mini": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "gpt-4o-mini-2024-07-18": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": True, "args": {}},
                    "gpt-4-turbo": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": False, "args": {}},
                    "gpt-4-turbo-2024-04-09": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": False, "args": {}},
                    "gpt-4-0125-preview": {"formatter": "AFormatterGPT", "contextWindow": 128000, "systemAsUser": False, "args": {}},
                    "gpt-4-turbo-preview": {"formatter": "AFormatterGPT", "contextWindow": 128000, "systemAsUser": False, "args": {}},
                    "gpt-4-1106-preview": {"formatter": "AFormatterGPT", "contextWindow": 128000, "systemAsUser": False, "args": {}},
                    "gpt-4-vision-preview": {"formatter": "AFormatterGPTVision", "contextWindow": 128000, "systemAsUser": False, "args": {}},
                    "gpt-4": {"formatter": "AFormatterGPT", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "gpt-4-32k": {"formatter": "AFormatterGPT", "contextWindow": 32768, "systemAsUser": False, "args": {}},
                    "gpt-4-0613": {"formatter": "AFormatterGPT", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "gpt-4-32k-0613": {"formatter": "AFormatterGPT", "contextWindow": 32768, "systemAsUser": False, "args": {}},
                    "gpt-4-0314": {"formatter": "AFormatterGPT", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "gpt-4-32k-0314": {"formatter": "AFormatterGPT", "contextWindow": 32768, "systemAsUser": False, "args": {}},
                }
            },
            "groq": {
                "modelWrapper": "AModelChatGPT",
                "apikey": None,
                "baseURL": "https://api.groq.com/openai/v1",
                "modelList": {
                    "llama3-8b-8192": {"formatter": "AFormatterGPT", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "llama3-70b-8192": {"formatter": "AFormatterGPT", "contextWindow": 8192, "systemAsUser": False, "args": {}},
                    "llama2-70b-4096": {"formatter": "AFormatterGPT", "contextWindow": 4096, "systemAsUser": False, "args": {}},
                    "mixtral-8x7b-32768": {"formatter": "AFormatterGPT", "contextWindow": 32768, "systemAsUser": False, "args": {}},
                    "gemma-7b-it": {"formatter": "AFormatterGPT", "contextWindow": 8192, "systemAsUser": False, "args": {}}
                }
            },
            "openrouter": {
                "modelWrapper": "AModelChatGPT",
                "apikey": None,
                "baseURL": "https://openrouter.ai/api/v1",
                "modelList": {}
            },
            "deepseek": {
                "modelWrapper": "AModelChatGPT",
                "apikey": None,
                "baseURL": "https://api.deepseek.com",
                "modelList": {
                    "deepseek-chat": {"formatter": "AFormatterGPT", "contextWindow": 32768, "systemAsUser": False, "args": {}},
                    "deepseek-coder": {"formatter": "AFormatterGPT", "contextWindow": 16384, "systemAsUser": False, "args": {}}
                }
            },
            "mistral": {
                    "modelWrapper": "AModelMistral",
                    "apikey": None,
                    "modelList": {
                        "mistral-small-latest": {"formatter": "AFormatterGPT", "contextWindow": 32764, "systemAsUser": True, "args": {}},
                        "mistral-medium-latest": {"formatter": "AFormatterGPT", "contextWindow": 32764, "systemAsUser": True, "args": {}},
                        "mistral-large-latest": {"formatter": "AFormatterGPT", "contextWindow": 32764, "systemAsUser": True, "args": {}}
                    }
            },
            "anthropic": {
                    "modelWrapper": "AModelAnthropic",
                    "apikey": None,
                    "baseURL": None,
                    "modelList": {
                        "claude-instant-1.2": {"formatter": "AFormatterGPT", "contextWindow": 100000, "systemAsUser": True, "args": {}},
                        "claude-2.0": {"formatter": "AFormatterGPT", "contextWindow": 100000, "systemAsUser": True, "args": {}},
                        "claude-2.1": {"formatter": "AFormatterGPT", "contextWindow": 200000, "systemAsUser": True, "args": {}},
                        "claude-3-sonnet-20240229": {"formatter": "AFormatterClaudeVision", "contextWindow": 200000, "systemAsUser": True, "args": {}},
                        "claude-3-opus-20240229": {"formatter": "AFormatterClaudeVision", "contextWindow": 200000, "systemAsUser": True, "args": {}},
                        "claude-3-5-sonnet-20240620": {"formatter": "AFormatterClaudeVision", "contextWindow": 200000, "systemAsUser": True, "args": {}},
                        "claude-3-5-sonnet-20241022": {"formatter": "AFormatterClaudeVision", "contextWindow": 200000, "systemAsUser": True, "args": {}},
                        "claude-3-5-haiku-20241022": {"formatter": "AFormatterGPT", "contextWindow": 200000, "systemAsUser": True, "args": {}}
                    }
            }
        }
        self.InitOpenRouterCfg()
        self.temperature = 0.0
        self.flashAttention2 = False
        self.speechOn = False
        self.ttsDevice = "cpu"
        self.sttDevice = "cpu"
        self.contextWindowRatio = 0.6
        if 'nt' == os.name:
            self.services = {
                "storage": {"cmd": "python -m frasier.modules.AStorageVecDB --addr=tcp://127.0.0.1:59001", "addr": "tcp://127.0.0.1:59001"},
                "browser": {"cmd": "python -m frasier.modules.ABrowser --addr=tcp://127.0.0.1:59002", "addr": "tcp://127.0.0.1:59002"},
                "arxiv": {"cmd": "python -m frasier.modules.AArxiv --addr=tcp://127.0.0.1:59003", "addr": "tcp://127.0.0.1:59003"},
                "google": {"cmd": "python -m frasier.modules.AGoogle --addr=tcp://127.0.0.1:59004", "addr": "tcp://127.0.0.1:59004"},
                "duckduckgo": {"cmd": "python -m frasier.modules.ADuckDuckGo --addr=tcp://127.0.0.1:59005", "addr": "tcp://127.0.0.1:59005"},
                "scripter": {"cmd": "python -m frasier.modules.AScripter --addr=tcp://127.0.0.1:59000", "addr": "tcp://127.0.0.1:59000"},
                "speech": {"cmd": "python -m frasier.modules.ASpeech --addr=tcp://127.0.0.1:59006", "addr": "tcp://127.0.0.1:59006"},
                "computer": {"cmd": "python -m frasier.modules.AComputer --addr=tcp://127.0.0.1:59007", "addr": "tcp://127.0.0.1:59007"},
            }
        else:
            self.services = {
                "storage": {"cmd": "python3 -m frasier.modules.AStorageVecDB --addr=ipc:///tmp/frasierStorage.ipc", "addr": "ipc:///tmp/frasierStorage.ipc"},
                "browser": {"cmd": "python3 -m frasier.modules.ABrowser --addr=ipc:///tmp/ABrowser.ipc", "addr": "ipc:///tmp/ABrowser.ipc"},
                "arxiv": {"cmd": "python3 -m frasier.modules.AArxiv --addr=ipc:///tmp/AArxiv.ipc", "addr": "ipc:///tmp/AArxiv.ipc"},
                "google": {"cmd": "python3 -m frasier.modules.AGoogle --addr=ipc:///tmp/AGoogle.ipc", "addr": "ipc:///tmp/AGoogle.ipc"},
                "duckduckgo": {"cmd": "python3 -m frasier.modules.ADuckDuckGo --addr=ipc:///tmp/ADuckDuckGo.ipc", "addr": "ipc:///tmp/ADuckDuckGo.ipc"},
                "scripter": {"cmd": "python3 -m frasier.modules.AScripter --addr=tcp://127.0.0.1:59000", "addr": "tcp://127.0.0.1:59000"},
                "speech": {"cmd": "python3 -m frasier.modules.ASpeech --addr=ipc:///tmp/ASpeech.ipc", "addr": "ipc:///tmp/ASpeech.ipc"},
                "computer": {"cmd": "python3 -m frasier.modules.AComputer --addr=ipc:///tmp/AComputer.ipc", "addr": "ipc:///tmp/AComputer.ipc"},
            }
        return

    def InitOpenRouterCfg(self):
        try:
            response = requests.get("https://openrouter.ai/api/v1/models")
            response.raise_for_status()
            json = response.json()
            for model in json['data']:
                self.models['openrouter']['modelList'][model['id']] = {"formatter": {"text->text": "AFormatterGPT", "text+image->text": "AFormatterGPTVision"}[model['architecture']['modality']],
                                                                       "contextWindow": int(model['context_length']),
                                                                       "systemAsUser": True,
                                                                       "args": {"extra_headers": {"HTTP-Referer": "https://github.com/myshell-ai/frasier", "X-Title": "frasier"}}}
        except Exception as e:
            print(f"InitOpenRouterCfg() FAILED, skip this part and do not set it again. EXCEPTION: {str(e)}")
        return
    
    def Initialize(self):
        print(colored("********************** Initialize *****************************", "yellow"))
        configFile = appdirs.user_config_dir("frasier", "Steven Lu")
        print(f"config.json is located at {configFile}")
        try:
            os.makedirs(configFile)
        except OSError as e:
            pass
        configFile = os.path.join(configFile, "config.json")
        
        oldDict = self.Load(configFile)
        self.Update(oldDict)
        self.Store(configFile)

        print(colored("********************** End of Initialization *****************************", "yellow"))
        return

    def Check4Update(self, modelID):
        modelIDs = [modelID] if "" != modelID else list(self.agentModelConfig.values())
        configFile = os.path.join(appdirs.user_config_dir("frasier", "Steven Lu"), "config.json")
        for id in modelIDs:
            modelType = id[:id.find(":")]
            modelName = id[id.find(":")+1:]
            if (modelType not in self.models) or (modelName not in self.models[modelType]['modelList']):
                print(f"The specified model ID '{id}' was not found in the configuration; you need to configure it in '{configFile}' beforehand.")
                sys.exit(0)
            if ("apikey" in self.models[modelType] and (self.models[modelType]["apikey"] is None)):
                key = input(colored(f"Your {modelType} api-key (press Enter if not): ", "green"))
                self.models[modelType]["apikey"] = key if 1 < len(key) else None
                self.Store(configFile)
        return
    
    def Update(self, cfgDict: dict):
        self.__dict__ = self.Merge("", self.__dict__, cfgDict)
        return
    
    def Merge(self, key, template, reference):
        if (type(template) == dict) and (type(reference)==dict):
            if key in ['models', 'modelList', 'services']:
                return {k: self.Merge(k, template[k], reference[k]) if ((k in template) and (k in reference)) else v for k, v in {**reference, **template}.items()}
            elif key in ['agentModelConfig']:
                return reference
            else:
                return {k: self.Merge(k, v, reference[k]) if k in reference else v for k,v in template.items()}
        else:
            return reference
    
    def Load(self, configFile: str) -> dict:
        if not os.path.exists(configFile):
            print(f"config.json not found, let's create a new one: '{configFile}'.")
            self.Store(configFile)
        with open(configFile, "r") as f:
            return json.load(f)
    
    def Store(self, configFile: str):
        with open(configFile, "w") as f:
            json.dump(self.__dict__, f, indent=2)
        return
    
    
config = AConfig()
