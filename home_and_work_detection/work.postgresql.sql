SELECT
    device_id, cell_id, count(*) AS count
FROM
    cdr
WHERE
    -- weekdays, 0 is Sunday, 6 is Saturday
    mod(extract(dow from cdr.timestamp)::integer, 6) > 0
AND
    -- Good Friday
    cdr.timestamp::date != '2017-04-14'
AND
    -- Easter Monday
    cdr.timestamp::date != '2017-04-17'
AND
    cdr.timestamp::time >= '09:00:00'
AND
    cdr.timestamp::time <= '16:00:00'
GROUP BY
    device_id, cell_id
ORDER BY
    device_id, count DESC;
