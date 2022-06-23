import React, { useEffect, useState } from 'react';
import { NoContent, Loader, Pagination } from 'UI';
import Select from 'Shared/Select';
import cn from 'classnames';
import { useStore } from 'App/mstore';
import SessionItem from 'Shared/SessionItem';
import { observer, useObserver } from 'mobx-react-lite';
import { DateTime } from 'luxon';
import { debounce } from 'App/utils';
import useIsMounted from 'App/hooks/useIsMounted'
import AnimatedSVG, { ICONS } from 'Shared/AnimatedSVG/AnimatedSVG';

interface Props {
    className?: string;
}
function WidgetSessions(props: Props) {
    const { className = '' } = props;
    const [activeSeries, setActiveSeries] = useState('all');
    const [data, setData] = useState<any>([]);
    const isMounted = useIsMounted();
    const [loading, setLoading] = useState(false);
    const filteredSessions = getListSessionsBySeries(data, activeSeries);
    const { dashboardStore, metricStore } = useStore();
    const filter = useObserver(() => dashboardStore.drillDownFilter);
    const widget: any = useObserver(() => metricStore.instance);
    // const drillDownPeriod = useObserver(() => dashboardStore.drillDownPeriod);
    const startTime = DateTime.fromMillis(filter.startTimestamp).toFormat('LLL dd, yyyy HH:mm');
    const endTime = DateTime.fromMillis(filter.endTimestamp).toFormat('LLL dd, yyyy HH:mm');
    // const [timestamps, setTimestamps] = useState<any>({
    //     startTimestamp: 0,
    //     endTimestamp: 0,
    // });
    const [seriesOptions, setSeriesOptions] = useState([
        { label: 'All', value: 'all' },
    ]);

    const writeOption = ({ value }: any) => setActiveSeries(value.value);
    useEffect(() => {
        if (!data) return;
        const seriesOptions = data.map((item: any) => ({
            label: item.seriesName,
            value: item.seriesId,
        }));
        setSeriesOptions([
            { label: 'All', value: 'all' },
            ...seriesOptions,
        ]);
    }, [data]);

    const fetchSessions = (metricId: any, filter: any) => {
        if (!isMounted()) return;
        setLoading(true)
        widget.fetchSessions(metricId, filter).then((res: any) => {
            setData(res)
        }).finally(() => {
            setLoading(false)
        });
    }
    const debounceRequest: any = React.useCallback(debounce(fetchSessions, 1000), []);

    const depsString = JSON.stringify(widget.series);
    useEffect(() => {
        debounceRequest(widget.metricId, { ...filter, series: widget.toJsonDrilldown(), page: metricStore.sessionsPage, limit: metricStore.sessionsPageSize });
    }, [filter.startTimestamp, filter.endTimestamp, filter.filters, depsString, metricStore.sessionsPage]);

    // useEffect(() => {
    //     const timestamps = drillDownPeriod.toTimestamps();
    //     // console.log('timestamps', timestamps);
    //     debounceRequest(widget.metricId, { startTime: timestamps.startTimestamp, endTime: timestamps.endTimestamp, series: widget.toJsonDrilldown(), page: metricStore.sessionsPage, limit: metricStore.sessionsPageSize });
    // }, [drillDownPeriod]);

    return useObserver(() => (
        <div className={cn(className)}>
            <div className="flex items-center justify-between">
                <div className="flex items-baseline">
                    <h2 className="text-2xl">Sessions</h2>
                    <div className="ml-2 color-gray-medium">between <span className="font-medium color-gray-darkest">{startTime}</span> and <span className="font-medium color-gray-darkest">{endTime}</span> </div>
                </div>

                { widget.metricType !== 'table' && (
                    <div className="flex items-center ml-6">
                        <span className="mr-2 color-gray-medium">Filter by Series</span>
                        <Select
                            options={ seriesOptions }
                            defaultValue={ 'all' }
                            onChange={ writeOption }
                            plain
                        />
                    </div>
                )}
            </div>

            <div className="mt-3 bg-white p-3 rounded border">
                <Loader loading={loading}>
                    <NoContent
                        title={
                            <div className="flex flex-col items-center justify-center">
                                <AnimatedSVG name={ICONS.NO_RESULTS} size="170" />
                                <div className="mt-6 text-2xl">No recordings found</div>
                            </div>
                        }
                        show={filteredSessions.sessions.length === 0}
                    >
                        {filteredSessions.sessions.map((session: any) => (
                            <>
                                <SessionItem key={ session.sessionId } session={ session }  />
                                <div className="border-b" />
                            </>
                        ))}

                        <div className="w-full flex items-center justify-center py-6">
                            <Pagination
                                page={metricStore.sessionsPage}
                                totalPages={Math.ceil(filteredSessions.total / metricStore.sessionsPageSize)}
                                onPageChange={(page: any) => metricStore.updateKey('sessionsPage', page)}
                                limit={metricStore.sessionsPageSize}
                                debounceRequest={500}
                            />
                        </div>
                    </NoContent>
                </Loader>
            </div>
        </div>
    ));
}

const getListSessionsBySeries = (data: any, seriesId: any) => {
    const arr: any = { sessions: [], total: 0 };
    data.forEach((element: any) => {
        if (seriesId === 'all') {
            const sessionIds = arr.sessions.map((i: any) => i.sessionId);
            arr.sessions.push(...element.sessions.filter((i: any) => !sessionIds.includes(i.sessionId)));
            arr.total = element.total
        } else {
            if (element.seriesId === seriesId) {
                arr.sessions.push(...element.sessions)
                arr.total = element.total
            }
        }
    });
    return arr;
}

export default observer(WidgetSessions);
