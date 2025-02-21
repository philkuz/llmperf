export GIMLET_CONTROLPLANE_BASE="https://localhost:60002"
export GIMLET_API_KEY=""
export GIMLET_DEVICE_ID=""

# Script to warm-up the gimlet controlplane.
curl -X GET \
  "$GIMLET_CONTROLPLANE_BASE/v1/chat/completions?deviceID=$GIMLET_DEVICE_ID" \
  -H "Authorization: Bearer $GIMLET_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "unknown",
    "messages": [
      {"role": "system", "content": ""},
      {"role": "user", "content": "test-prompt"}
    ],
    "stream": true
  }' \
  -k >/dev/null 2>/dev/null

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

