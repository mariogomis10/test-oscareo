
WITH cte_file_downloads AS (
  SELECT
    f.project,
    f.file.version,
    f.country_code,
    f.timestamp
  FROM
    `bigquery-public-data.pypi.file_downloads` f
  WHERE DATE(timestamp) = CURRENT_DATE()
  ORDER BY 1, 2, 3, 4 
),

cte_distribution_metadata AS(
  SELECT
    d.name,
    d.version,
    d.requires_dist AS dependencies,
    ARRAY_LENGTH(d.requires_dist) AS dependencies_count,
    COALESCE(d.size, 0) AS package_size
  FROM
    `bigquery-public-data.pypi.distribution_metadata` d

    -- Ce filtre a pour seul objectif de réduire le volume de données à traiter pour l'exemple
  WHERE
    d.version IN ('1.17.0', '0.4.0', '2.2.2', '1.26.4', '2.25.1')
    AND d.name IN ('botocore', 's3transfer', 'awscli', 'urllib3', 'requests') 
    )


SELECT
  fd.timestamp,
  fd.country_code,
  fd.project,
  fd.version,
  dependencies,
  dependencies_count,
  ROUND(package_size / (1024 * 1024), 2) AS size_mb,
  ROUND(package_size / (1024 * 1024 * 1024), 2) AS size_gb
FROM
  cte_file_downloads AS fd
INNER JOIN
  cte_distribution_metadata AS dm
ON
  fd.project = dm.name AND fd.version = dm.version
