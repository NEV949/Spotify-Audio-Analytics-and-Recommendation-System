# Submit the PySpark clustering job on the same Docker network as namenode.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }
$network = docker inspect namenode -f "{{range `$k, `$v := .NetworkSettings.Networks}}{{`$k}}{{end}}"
if (-not $network) { throw "namenode is not running. Start Hadoop first: docker compose up -d" }

docker run --rm --network $network `
  -v "${root}/jobs:/jobs" `
  apache/spark:3.5.1 `
  /opt/spark/bin/spark-submit --master local[*] `
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 `
  --conf spark.hadoop.dfs.client.use.datanode.hostname=true `
  /jobs/spotify_pipeline.py @args
