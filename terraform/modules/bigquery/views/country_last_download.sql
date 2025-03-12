with cte_1 as (
  SELECT 
  `timestamp` as date_time, 
  DATE(`timestamp`) as day, 
  country_code, 
  `project` as project_name, 
  version, 
  dependencies, 
  dependencies_count, 
  size_mb, 
  size_gb
FROM `${project_id}.${dataset_id}.${table_id}`
),

cte_2 as (
  SELECT 
    date_time, 
    day, 
    country_code, 
    project_name, 
    version, 
    dependencies, 
    dependencies_count, 
    size_mb, 
    size_gb,
    rank() over (partition by country_code, project_name, day order by date_time DESC) as rank_last_download
  FROM cte_1
)

  SELECT 
    date_time, 
    day, 
    country_code, 
    project_name, 
    version, 
    dependencies, 
    dependencies_count, 
    size_mb, 
    size_gb
  FROM cte_2
  where rank_last_download = 1

