export OPENAI_API_BASE=""
export OPENAI_API_KEY="EMPTY"

python token_benchmark_ray.py \
--model "meta-llama/Meta-Llama-3-8B-Instruct" \
--mean-input-tokens 550 \
--stddev-input-tokens 150 \
--mean-output-tokens 250 \
--stddev-output-tokens 10 \
--max-num-completed-requests 8000 \
--timeout 600 \
--num-concurrent-requests 250 \
--results-dir "result_outputs" \
--llm-api openai \
--additional-sampling-params '{}'

