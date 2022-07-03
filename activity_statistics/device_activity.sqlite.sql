SELECT
    device_id,
    count(*) AS activity_count
FROM
    cdr
WHERE
    timestamp >= '2017-04-01 00:00:00'
AND
    timestamp < '2017-04-30 24:00:00'
GROUP BY
    device_id
ORDER BY
    device_id

