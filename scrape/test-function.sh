curl localhost:8080 \
  -X POST \
  -H "Content-Type: application/json" \
  -H "ce-id: 123451234512345" \
  -H "ce-specversion: 1.0" \
  -H "ce-time: 2020-01-02T12:34:56.789Z" \
  -H "ce-type: google.cloud.pubsub.topic.v1.messagePublished" \
  -H "ce-source: //pubsub.googleapis.com/projects/xmas-scrape/topics/run-nightly" \
  -d "{
        \"message\": {
          \"data\": \"\"
        },
        \"subscription\": \"projects/xmas-scrape/subscriptions/run-nightly\"
      }"

