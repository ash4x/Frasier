FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /scripter

COPY frasier/__init__.py /scripter/frasier/__init__.py
COPY frasier/common/__init__.py /scripter/frasier/common/__init__.py
COPY frasier/common/ADataType.py /scripter/frasier/common/ADataType.py
COPY frasier/common/lightRPC.py /scripter/frasier/common/lightRPC.py
COPY frasier/modules/__init__.py /scripter/frasier/modules/__init__.py
COPY frasier/modules/AScripter.py /scripter/frasier/modules/AScripter.py
COPY frasier/modules/AScrollablePage.py /scripter/frasier/modules/AScrollablePage.py

RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install pillow
RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install requests
RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install numpy
RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install pyzmq
RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install av

EXPOSE 59000-59200


CMD ["python3", "-m", "frasier.modules.AScripter", "--incontainer", "--addr=tcp://0.0.0.0:59000"]
