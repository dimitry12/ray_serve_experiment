from starlette.requests import Request

import ray
from ray import serve
from ray.serve.handle import DeploymentHandle
import asyncio
from typing import List


@serve.deployment(num_replicas=1, ray_actor_options={"num_cpus": 2.0,
                                                     "num_gpus": 0.0})  # require 2.0 CPUs to force the deployment to go to the worker-node
class TextGenerator:
    def __init__(self):
        # can import packages not available in Ray "driver", only in "worker"
        from transformers import GPTNeoXForCausalLM, AutoTokenizer

        self.model = GPTNeoXForCausalLM.from_pretrained(
            "EleutherAI/pythia-70m-deduped",
            revision="step3000",
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            "EleutherAI/pythia-70m-deduped",
            revision="step143000",
            padding_side="left" # for batching
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token # for batching

    @serve.batch(max_batch_size=3, batch_wait_timeout_s=1.0)
    async def generate(self, texts: List[str]) -> List[str]:
        inputs = self.tokenizer(texts, return_tensors="pt")
        tokens = self.model.generate(**inputs, do_sample=True, temperature=1.0)
        print(f"LLM inputs shape: {inputs['input_ids'].shape}")
        outputs = self.tokenizer.batch_decode(tokens, skip_special_tokens=True)

        return outputs


@serve.deployment(num_replicas=1, ray_actor_options={"num_cpus": 1.0,
                                                     "num_gpus": 0.0})  # require 2.0 CPUs to force the deployment to go to the worker-node
class OrchestratingPipeline:
    def __init__(self, generator: DeploymentHandle):
        self.generator = generator

    async def __call__(self, http_request: Request) -> str:
        text: str = await http_request.json()
        # make 6 calls in parallel

        results = await asyncio.gather(*[self.generator.generate.remote(text) for _ in range(6)]) # `@serve.batch`-decorated `.generate` takes single string as input

        return ", ".join(results)


# can't construct directly now that this is a Ray deployment
# async def test():
#     generator = TextGenerator()
#     print(generator.generate_text("Once upon a time"))

# A `Deployment` becomes an `Application` when bound
generator_app = TextGenerator.bind()
orchestrating_pipeline_app = OrchestratingPipeline.bind(generator_app)

# We can pass an application when `.bind`ing another application.
# Thus passed `Application` becomes a `DeploymentHandle` at runtime and
# its methods can be called remotely without using HTTP API. Aka composition.

if __name__ == "__main__":
    # only one `Application` is used as an entrypoint
    generator_deployment_handle: DeploymentHandle = serve.run(generator_app)


    async def test():
        # when inside Ray Serve instance, can use the deployment "directly" as-if composing
        print(await generator_deployment_handle.generate.remote("Once upon a time"))


    asyncio.run(test())

    # ray serve cluster stops at the end of the script
