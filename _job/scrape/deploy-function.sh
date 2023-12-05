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