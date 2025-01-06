#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import threading
import numpy
import inspect
import typing
import zmq
import pickle
import traceback
import frasier
from frasier.common.ADataType import *

WORKERS_ADDR="inproc://workers"
context=zmq.Context()

def SendMsg(conn,msg):
  conn.send(pickle.dumps(msg))
  return
  
def ReceiveMsg(conn):
  return pickle.loads(conn.recv())

class GenesisRPCServer(object):
  def __init__(self,objCls,objArgs,url,APIList):
    self.objCls=objCls
    self.objArgs=objArgs
    self.url=url
    self.objPool=dict()
    self.APIList=APIList
    self.context=context
    self.receiver = self.context.socket(zmq.ROUTER)
    self.receiver.bind(url)
    self.dealer = self.context.socket(zmq.DEALER)
    self.dealer.bind(WORKERS_ADDR)
    return
  
  def Run(self):
    try:
      for i in range(16):
        thread = threading.Thread(target=self.Worker, name="RPC-Worker-%d" % (i + 1))
        thread.daemon = True
        thread.start()

      zmq.device(zmq.QUEUE, self.receiver, self.dealer)
    except Exception as e:
      print('GenesisRPCServer:Run() FATAL EXCEPTION. ',self.url,', ',str(e))
      sys.exit(1)
    finally:
      self.receiver.close()
      self.dealer.close()
  
  def Worker(self):
    socket = self.context.socket(zmq.REP)
    socket.setsockopt(zmq.HEARTBEAT_IVL, 2000)
    socket.setsockopt(zmq.HEARTBEAT_TIMEOUT, 10000)
    socket.connect(WORKERS_ADDR)

    while True:
      msg=ReceiveMsg(socket)
      ret=None
      try:
        if ('clientID' in msg) and (msg['clientID'] not in self.objPool):
          ret = {"exception": KeyError(f"clientID {msg['clientID']} not exist.")}
        elif "GET_META" in msg:
          methods=inspect.getmembers(self.objCls, predicate=lambda x: (inspect.isfunction(x) and x.__name__ in self.APIList))
          ret={"META":{"methods": {methodName: str(inspect.signature(method)) for methodName, method in methods}}}
        elif "CREATE" in msg:
          newID = str(max([int(k) for k in self.objPool]) + 1) if self.objPool else '10000000'
          self.objPool[newID]=self.objCls(**self.objArgs)
          ret = {"clientID": newID}
        elif "DEL" in msg:
          del self.objPool[msg['clientID']]
        else:
          ret={'ret':(getattr(self.objPool[msg['clientID']],msg['function'])(*msg['args'], **msg['kwargs']))}
      except Exception as e:
        e.tb = ''.join(traceback.format_tb(e.__traceback__))
        ret={'exception':e}
        traceback.print_tb(e.__traceback__)
        print('Exception. msg: ',str(msg),'. Except: ',str(e))
      SendMsg(socket,ret)
    return


def makeServer(objCls,objArgs,url,APIList):
  return GenesisRPCServer(objCls,objArgs,url,APIList)

def AddMethod(kls,methodName,signature):
  tempNamespace = {k.__name__: k for k in typeInfo}
  tempNamespace["frasier"] = frasier
  tempNamespace["numpy"] = numpy
  tempNamespace["Any"] = typing.Any
  tempNamespace["Union"] = typing.Union
  tempNamespace["Optional"] = typing.Optional
  tempNamespace["List"] = typing.List
  tempNamespace["Tuple"] = typing.Tuple
  tempNamespace["Dict"] = typing.Dict
  tempNamespace["Set"] = typing.Set
  tempNamespace["Callable"] = typing.Callable
  tempNamespace["TypeVar"] = typing.TypeVar
  tempNamespace["Generic"] = typing.Generic
  
  exec(f"def tempFunc{signature}: pass", tempNamespace)
  tempFunc = tempNamespace['tempFunc']
  newSignature = inspect.Signature(parameters=[inspect.Parameter(name=t.name, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=t.annotation) for p,t in inspect.signature(tempFunc).parameters.items()],
                                   return_annotation=inspect.signature(tempFunc).return_annotation)

  def methodTemplate(self,*args,**kwargs):
    return self.RemoteCall(methodName,args,kwargs)
  methodTemplate.__signature__ = newSignature
  setattr(kls,methodName,methodTemplate)

def makeClient(url,returnClass=False):
  class GenesisRPCClientTemplate(object):
    def __init__(self):
      self.url=url
      self.context=context
      ret=self.Send({'CREATE':''})
      if "exception" in ret:
        raise ret["exception"]
      self.clientID=ret['clientID']
      return
    
    def Send(self, msg):
      with self.context.socket(zmq.REQ) as socket:
        socket.setsockopt(zmq.CONNECT_TIMEOUT, 10000)
        socket.setsockopt(zmq.HEARTBEAT_IVL, 2000)
        socket.setsockopt(zmq.HEARTBEAT_TIMEOUT, 10000)
        socket.connect(url)
        SendMsg(socket, msg)
        return ReceiveMsg(socket)
    
    def RemoteCall(self,funcName,args,kwargs):
      ret = self.Send({'clientID': self.clientID, 'function':funcName, 'args':args, "kwargs": kwargs})
      if 'exception' in ret:
        raise ret['exception']
      return ret['ret']
    
    def __del__(self):
      if hasattr(self, "clientID"):
        self.Send({'DEL':'', 'clientID': self.clientID})
      return
  
  with context.socket(zmq.REQ) as socket:
    socket.setsockopt(zmq.CONNECT_TIMEOUT, 10000)
    socket.setsockopt(zmq.SNDTIMEO, 10000) 
    socket.setsockopt(zmq.RCVTIMEO, 10000)
    socket.connect(url)
    SendMsg(socket,{'GET_META':''})
    ret=ReceiveMsg(socket)
  for funcName, signature in ret['META']['methods'].items():
    AddMethod(GenesisRPCClientTemplate,funcName,signature)
  return GenesisRPCClientTemplate if returnClass else GenesisRPCClientTemplate()
