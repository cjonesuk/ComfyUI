import os
import uuid

import jwt
import pytest

from comfy.client.embedded_comfy_client import EmbeddedComfyClient, ServerStub
from comfy.client.sdxl_with_refiner_workflow import sdxl_workflow_with_refiner
from comfy.component_model.make_mutable import make_mutable
from comfy.component_model.queue_types import QueueItem, QueueTuple, TaskInvocation
from comfy.distributed.distributed_prompt_worker import DistributedPromptWorker
from testcontainers.rabbitmq import RabbitMqContainer

# fixes issues with running the testcontainers rabbitmqcontainer on Windows
os.environ["TC_HOST"] = "localhost"


@pytest.mark.asyncio
async def test_sign_jwt_auth_none():
    client_id = str(uuid.uuid4())
    user_token_str = jwt.encode({"sub": client_id}, None, algorithm="none")
    user_token = jwt.decode(user_token_str, None, algorithms=["none"], options={"verify_signature": False})
    assert user_token["sub"] == client_id


@pytest.mark.asyncio
async def test_basic_queue_worker() -> None:
    # there are lots of side effects from importing that we have to deal with

    with RabbitMqContainer("rabbitmq:latest") as rabbitmq:
        params = rabbitmq.get_connection_params()
        async with DistributedPromptWorker(connection_uri=f"amqp://guest:guest@127.0.0.1:{params.port}") as worker:
            # this unfortunately does a bunch of initialization on the test thread
            from comfy.cmd.execution import validate_prompt
            from comfy.distributed.distributed_prompt_queue import DistributedPromptQueue
            # now submit some jobs
            distributed_queue = DistributedPromptQueue(ServerStub(), is_callee=False, is_caller=True,
                                                       connection_uri=f"amqp://guest:guest@127.0.0.1:{params.port}")
            await distributed_queue.init()
            prompt = make_mutable(sdxl_workflow_with_refiner("test", inference_steps=1, refiner_steps=1))
            validation_tuple = validate_prompt(prompt)
            item_id = str(uuid.uuid4())
            queue_tuple: QueueTuple = (0, item_id, prompt, {}, validation_tuple[2])
            res: TaskInvocation = await distributed_queue.put_async(QueueItem(queue_tuple, None))
            assert res.item_id == item_id
            assert len(res.outputs) == 1
            assert res.status is not None
            assert res.status.status_str == "success"
            await distributed_queue.close()