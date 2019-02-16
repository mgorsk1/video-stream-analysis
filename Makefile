reset:
	curl -X DELETE localhost:9200/*
	rm -f ./output/*
	rm -f ./log/*
	python3 bin/clean_redis.py
	gsutil rm gs://police_notifier/*

