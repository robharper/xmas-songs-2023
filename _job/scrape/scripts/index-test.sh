curl localhost:8080 \
  -X POST \
  -H "Content-Type: application/json" \
  -H "ce-id: 123451234512345" \
  -H "ce-specversion: 1.0" \
  -H "ce-time: 2020-01-02T12:34:56.789Z" \
  -H "ce-type: google.cloud.storage.object.v1.finalized" \
  -H "ce-source: //storage.googleapis.com/projects/_/buckets/xmas-scrape-data" \
  -H "ce-subject: objects/MY_FILE.txt" \
  -d "{
        \"bucket\": \"xmas-scrape-data\",
        \"contentType\": \"application/json\",
        \"kind\": \"storage#object\",
        \"md5Hash\": \"...\",
        \"metageneration\": \"1\",
        \"name\": \"$1\",
        \"size\": \"352\",
        \"storageClass\": \"MULTI_REGIONAL\",
        \"timeCreated\": \"2020-04-23T07:38:57.230Z\",
        \"timeStorageClassUpdated\": \"2020-04-23T07:38:57.230Z\",
        \"updated\": \"2020-04-23T07:38:57.230Z\"
      }"