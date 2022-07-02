SELECT
    device_id, cell_id, count(*) AS count
FROM
    cdr
WHERE
(
        -- weekends, 0 is Sunday, 6 is Saturday
        mod(cast(strftime("%w", cdr.timestamp) AS INT), 6) = 0
    OR
        -- Good Friday
        date(cdr.timestamp) = '2017-04-14'
    OR
        -- Easter Monday
        date(cdr.timestamp) = '2017-04-17'
    )
OR
    (
        -- weekdays, 0 is Sunday, 6 is Saturday
        mod(cast(strftime("%w", cdr.timestamp) AS INT), 6) > 0
    AND
        -- Good Friday
        date(cdr.timestamp) != '2017-04-14'
    AND
        -- Easter Monday
        date(cdr.timestamp) != '2017-04-17'
    AND
        (
            time(cdr.timestamp) >= '22:00:00'
        OR
            time(cdr.timestamp) <= '06:00:00'
        )
    )
GROUP BY
    device_id, cell_id
ORDER BY
    device_id, count DESC;

