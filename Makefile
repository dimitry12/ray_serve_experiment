start_rayserve_dev: # single-node only
	serve run main:orchestrating_pipeline_app # run one specific app which wraps "entrypoint" deployment

run_rayserve_and_exit:
	python main.py



run_client:
	python client.py



start_raycluster_head:
	RAY_ENABLE_WINDOWS_OR_OSX_CLUSTER=1 ray start --head --num-cpus=1 # it runs in the background

start_raycluster_node:
	ray start --address='auto' --num-cpus=2 # it runs in the background

stop_raycluster:
	ray stop

build_rayserve_config:
	serve build main:orchestrating_pipeline_app -o main__orchestrating_pipeline_app.serve_config.yaml

deploy_rayserve_config: build_rayserve_config
	# app is importable in Ray Cluster in context of this repo
	serve deploy main__orchestrating_pipeline_app.serve_config.yaml

run_experiment: start_raycluster_head start_raycluster_node build_rayserve_config deploy_rayserve_config run_client