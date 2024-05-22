## Usage

1. `make run_experiment`, which
   - starts a Ray cluster head node configured with `1.0` logical CPU
   - starts a Ray cluster worker node configured with `2.0` logical CPUs
   - generates Ray Serve config for an app with two deployments:
     1. `OrchestratingPipeline` (configured to require `1.0` CPU), which for each request makes multiple calls to
     2. LLM-powered `TextGenerator` (configured to require `2.0` CPUs). This is one uses Ray Serve's dynamic batching feature.
   - deploys the Ray Serve app to the cluster
2. Make observations at http://127.0.0.1:8265/:
   - observe that two deployments got scheduled on different nodes in the cluster
   - observe that `OrchestratingPipeline` received 1 request from the client which took 919.8ms
   - observe that `TextGenerator` received 6 simultaneous requests from `OrchestratingPipeline` taking: 553.3ms, 553.8ms, 553.9ms, 906.5ms, 906.6ms, 906.4ms
   - observe that across 6 requests `TextGenerator` logged **2** LLM inference calls, with batch size 3 each
3. `make stop_raycluster` to stop the Ray cluster.

## TODO

- [ ] what's the transport for cross-node communication when using deployment-handle composition in Ray Serve?