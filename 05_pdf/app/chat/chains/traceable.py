from langfuse import get_client, Langfuse
from langfuse.langchain import CallbackHandler

langfuse = get_client()

class TraceableChain:
    def __call__(self, *args, **kwargs):
        langfuse_handler = CallbackHandler()

        predefined_trace_id = Langfuse.create_trace_id(
            seed=self.metadata.get("conversation_id")
        )

        with langfuse.start_as_current_observation(
            as_type="span",
            name=self.metadata.get("conversation_id"),
            trace_context={"trace_id": predefined_trace_id}
        ) as span:
            span.update_trace(
                name=self.metadata.get("conversation_id"),
                metadata=self.metadata
            )
            
            callbacks = kwargs.get("callbacks", [])
            callbacks.append(langfuse_handler)
            kwargs["callbacks"] = callbacks
            
            result = super().__call__(*args, **kwargs)
        
        return result