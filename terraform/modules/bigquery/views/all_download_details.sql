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
  size_gb,
  CASE
    WHEN SUBSTRING(path, -3) = '.gz' THEN true
    ELSE false
  END AS gzip  
FROM `${project_id}.${dataset_id}.${table_id}`
),

cte_2 as (
  SELECT 
    day, 
    country_code, 
    project_name, 
    version, 
    dependencies, 
    dependencies_count, 
    size_mb, 
    size_gb,
    gzip,
    date_time, 
    LAG(date_time) over (partition by project_name order by date_time) as date_time_previous
  FROM cte_1
)

  SELECT 
    day, 
    country_code, 
    project_name, 
    version, 
    dependencies, 
    dependencies_count, 
    size_mb, 
    size_gb,
    gzip,
    date_time, 
    date_time_previous,
    DATETIME_DIFF(date_time, date_time_previous, SECOND) time_previous_second
  FROM cte_2