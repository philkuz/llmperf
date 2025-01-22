export OPENAI_API_BASE=""
export OPENAI_API_KEY="EMPTY"

python token_benchmark_ray.py \
--model "meta-llama/Llama-3.2-1B-Instruct" \
--mean-input-tokens 550 \
--stddev-input-tokens 150 \
--mean-output-tokens 150 \
--stddev-output-tokens 10 \
--max-num-completed-requests 30 \
--timeout 600 \
--num-concurrent-requests 1 \
--results-dir "result_outputs" \
--llm-api openai \
--additional-sampling-params '{}'

