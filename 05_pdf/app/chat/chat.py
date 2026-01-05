import os
from langchain_openai import ChatOpenAI
from app.chat.models import ChatArgs
from app.chat.vector_stores import retriever_map
from app.chat.llms import llm_map
from app.chat.memories import memory_map
from app.chat.chains.retrieval import StreamingConversationalRetrievalChain
from app.web.api import set_conversation_components, get_conversation_components
from app.chat.score import random_component_by_score


def build_chat(chat_args: ChatArgs):
    retriever_name, retriever = select_component("retriever", retriever_map, chat_args)
    llm_name, llm = select_component("llm", llm_map, chat_args)
    memory_name, memory = select_component("memory", memory_map, chat_args)

    set_conversation_components(
        chat_args.conversation_id,
        retriever=retriever_name,
        memory=memory_name,
        llm=llm_name
    )

    return StreamingConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        condense_question_llm=ChatOpenAI(api_key=os.environ["OPENAI_API_KEY"], streaming=False),
        metadata=chat_args.metadata,
    )

def select_component(component_type: str, component_map: dict, chat_args: ChatArgs) -> str:
    components = get_conversation_components(chat_args.conversation_id)
    
    prev_component = components.get(component_type)
    if prev_component:
        build_component = component_map.get(prev_component)
        return prev_component, build_component(chat_args)
    else:
        random_component = random_component_by_score(component_type, component_map)
        build_component = component_map.get(random_component)
        return random_component, build_component(chat_args)