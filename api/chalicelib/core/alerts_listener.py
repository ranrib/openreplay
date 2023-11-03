from chalicelib.utils import pg_client, helper


async def get_all_alerts():
    async with pg_client.PostgresClient(long_query=True) as cur:
        query = """SELECT -1 AS tenant_id,
                           alert_id,
                           projects.project_id,
                           detection_method,
                           query,
                           options,
                           (EXTRACT(EPOCH FROM alerts.created_at) * 1000)::BIGINT AS created_at,
                           alerts.name,
                           alerts.series_id,
                           filter,
                           change,
                           COALESCE(metrics.name || '.' || (COALESCE(metric_series.name, 'series ' || index)) || '.count',
                                    query ->> 'left')                             AS series_name
                    FROM public.alerts
                             INNER JOIN projects USING (project_id)
                             LEFT JOIN metric_series USING (series_id)
                             LEFT JOIN metrics USING (metric_id)
                    WHERE alerts.deleted_at ISNULL
                      AND alerts.active
                      AND projects.active
                      AND projects.deleted_at ISNULL
                      AND (alerts.series_id ISNULL OR metric_series.deleted_at ISNULL)
                    ORDER BY alerts.created_at;"""
        await cur.execute(query=query)
        all_alerts = await cur.fetchall()
        all_alerts = helper.list_to_camel_case(all_alerts)
    return all_alerts
