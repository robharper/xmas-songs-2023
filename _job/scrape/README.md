## Setup

**TODO: Move to terraform**

### Setup a Service Account
Create it
```
gcloud iam service-accounts create xmas-scraper --project xmas-scrape
```

Give it permissions:
```
# Allow it to upload to Cloud Storage
gcloud projects add-iam-policy-binding xmas-scrape --member="serviceAccount:xmas-scraper@xmas-scrape.iam.gserviceaccount.com" --role=roles/storage.objectCreator

# Allow it to invoke a Cloud Function
gcloud projects add-iam-policy-binding xmas-scrape --member="serviceAccount:xmas-scraper@xmas-scrape.iam.gserviceaccount.com" --role=roles/run.invoker

# Allow it to run BigQuery jobs
gcloud projects add-iam-policy-binding xmas-scrape --member="serviceAccount:xmas-scraper@xmas-scrape.iam.gserviceaccount.com" --role=roles/bigquery.jobUser
```




### Create a Cloud Storage Bucket
```
gcloud storage buckets create gs://xmas-scrape-data --project=xmas-scrape --default-storage-class=standard --location=northamerica-northeast2 --uniform-bucket-level-access
```

TODO: Give service account `Creator` IAM access

### Create a Pub/Sub Topic
To create a pubsub topic to trigger the cloud function, run:
```
gcloud pubsub topics create xmas-scrape_scrape
```

### Deploy the Cloud Function
```
gcloud functions deploy xmas-scrape-scraper \
--project=xmas-scrape \
--gen2 \
--runtime=python311 \
--region=northamerica-northeast1 \
--source=. \
--entry-point=scrape \
--trigger-topic=xmas-scrape_scrape \
--service-account=xmas-scraper@xmas-scrape.iam.gserviceaccount.com \
--env-vars-file .env.yaml
```

## Testing
### Local
Run the function in local mode:
```
cd _job
./run-function.sh
```

Simulate a pubsub event, run the function:
```
cd _job
./test-function.sh
```

### Deployed
To generate a quote for a specific day, run:
```
gcloud pubsub topics publish xmas-scrape_scrape --message="" --project=xmas-scrape
```

