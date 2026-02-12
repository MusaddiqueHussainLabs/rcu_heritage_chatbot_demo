# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import aiohttp
import os
from pathlib import Path
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
    CardFactory,
    MessageFactory
)
# from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env, ActionTypes, Activity, ActivityTypes, Attachment

from microsoft_agents.activity import (
    HeroCard,
    AnimationCard,
    AudioCard,
    ReceiptCard,
    ReceiptItem,
    ThumbnailCard,
    VideoCard,
    CardAction,
    CardImage,
    MediaUrl,
    ThumbnailUrl,
    Fact,
)

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import convert_to_messages

# from agents import supervisor
from agents import agent, image_search_agent
from response_schemas import AlulaResponse

load_dotenv()  # robrandao: todo
agents_sdk_config = load_configuration_from_env(environ)

UPLOAD_DIR = "data/uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        "Welcome to the RCU Heritage AI Assistant! "
        "I can help you explore the AlUla Collections - 100 Objects dataset through intelligent search and discovery."
    )
    return True

@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):

    try:

        # ---------------------------------
        # 1️⃣ IMAGE UPLOAD HANDLING
        # ---------------------------------
        if context.activity.attachments:
            
            attachment = context.activity.attachments[0]

            if attachment.content_type.startswith("image/"):

                image_url = attachment.content_url
                file_name = attachment.name or "uploaded_image.png"
                local_path = os.path.join(UPLOAD_DIR, file_name)
                
                # Download image
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            with open(local_path, "wb") as f:
                                f.write(await resp.read())

                
                local_path = os.path.abspath(local_path)  # Ensure absolute path for the tool
                # print(f"Invoking agent with image path: {local_path}")
                await context.send_activity("Analyzing image... please wait.")

                response = image_search_agent.invoke(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"search_by_image_and_explain(image_path='{local_path}')"
                                }
                            ]
                        }
                    )

                raw_output = response["messages"][-1].content
                # print(f"Raw output from agent: {raw_output}")
                MAX_LENGTH = 5000  # safe size

                if len(raw_output) > MAX_LENGTH:
                    raw_output = raw_output[:MAX_LENGTH] + "\n\n[Response truncated for size safety]"

                await context.send_activity(raw_output)

        # ---------------------------------
        # 2️⃣ TEXT QUERY HANDLING
        # ---------------------------------
        if context.activity.text:

            response = agent.invoke(
                {"messages": [{"role": "user", "content": context.activity.text}]}
            )

            structured = response["structured_response"]

            await context.send_activity(structured.answer)

            if structured.image_paths:
                url_image_path = os.path.join(
                    os.environ.get("IMAGE_BASE_URL", ""),
                    structured.image_paths[0]
                )

                reply = MessageFactory.text("")
                card = CardFactory.hero_card(
                    HeroCard(
                        title=structured.inv_no or "Related Artifact",
                        images=[CardImage(url=url_image_path)]
                    )
                )
                reply.attachments = [card]
                await context.send_activity(reply)

    except Exception as e:
        print(f"Error during agent execution: {e}", file=sys.stderr)
        traceback.print_exc()
        await context.send_activity("An error occurred while processing your request.")




@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
