export GIMLET_CONTROLPLANE_BASE="https://localhost:60002"
export GIMLET_API_KEY=""
export GIMLET_DEVICE_ID=""

python token_benchmark_ray.py \
--model "unknown" \
--mean-input-tokens 550 \
--stddev-input-tokens 150 \
--mean-output-tokens 150 \
--stddev-output-tokens 10 \
--max-num-completed-requests 20 \
--timeout 600 \
--num-concurrent-requests 1 \
--results-dir "result_outputs" \
--llm-api gimlet \
--additional-sampling-params '{}'


# python llm_correctness.py \
# --model "unknown" \
# --llm-api gimlet \
# --max-num-completed-requests 150 \
# --timeout 600 \
# --num-concurrent-requests 10 \
# --results-dir "result_outputs"

