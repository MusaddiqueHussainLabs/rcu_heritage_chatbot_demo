# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os.path as path
import re
import sys
import traceback
from dotenv import load_dotenv

from os import environ
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
# from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import convert_to_messages

# from agents import supervisor
from agents import agent

load_dotenv()  # robrandao: todo
agents_sdk_config = load_configuration_from_env(environ)

STORAGE = MemoryStorage()
ADAPTER = CloudAdapter()
# CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
# ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)
# AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **agents_sdk_config)

# robrandao: downloader?
AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, adapter=ADAPTER #, authorization=AUTHORIZATION, **agents_sdk_config
)

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity(
        "Welcome to the empty agent! "
        "This agent is designed to be a starting point for your own agent development."
    )
    return True


# @AGENT_APP.message(re.compile(r"^hello$"))
# async def on_hello(context: TurnContext, _state: TurnState):
#     await context.send_activity("Hello!")


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    try:
        context.streaming_response.queue_informative_update("Working on a response for you...")

        async for token, metadata in agent.astream(  
            {"messages": [{"role": "user", "content": context.activity.text}]},
            stream_mode="messages",
        ):
            if token.content and metadata["langgraph_node"] == "model":
    
                blocks = token.content_blocks
                
                for block in blocks:
                    # We only want model->text blocks (not tool calls)
                    if block["type"] == "text":
                        final_text = block["text"]
                        context.streaming_response.queue_text_chunk(final_text)
            

    except Exception as e:
        context.streaming_response.queue_text_chunk(f"Error during streaming: {e}")
        context.streaming_response.queue_text_chunk("An error occurred while generating the response. Please try again later.")
    finally:
        await context.streaming_response.end_stream()
    
    
    # await context.send_activity(f"you said: {context.activity.text}")


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
