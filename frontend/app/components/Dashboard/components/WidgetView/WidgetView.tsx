import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { useStore } from 'App/mstore';
import WidgetForm from '../WidgetForm';
import WidgetPreview from '../WidgetPreview';
import WidgetSessions from '../WidgetSessions';
import { Icon, BackLink, Loader } from 'UI';
import { useObserver } from 'mobx-react-lite';
import { withSiteId } from 'App/routes';
import WidgetName from '../WidgetName';
interface Props {
    history: any;
    match: any
    siteId: any
}
function WidgetView(props: Props) {
    const { match: { params: { siteId, dashboardId, metricId } } } = props;
    const [expanded, setExpanded] = useState(true);
    const { metricStore } = useStore();
    const widget = useObserver(() => metricStore.instance);
    const loading = useObserver(() => metricStore.isLoading);

    React.useEffect(() => {
        if (metricId && metricId !== 'create') {
            metricStore.fetch(metricId).then((metric) => {
                // metricStore.init(metric)
            });
        } else {
            metricStore.init();
        }
    }, [])

    const onBackHandler = () => {
        if (dashboardId) {
            props.history.push(withSiteId(`/dashboard/${dashboardId}`, siteId));    
        } else {
            props.history.push(withSiteId(`/metrics`, siteId));
        }
    }

    return useObserver(() => (
        <Loader loading={loading}>
            <div className="relative">
                <BackLink onClick={onBackHandler} vertical className="absolute" style={{ left: '-50px', top: '0px' }} />
                <div className="bg-white rounded border">
                    <div className="p-4 flex justify-between items-center">
                        <h1 className="mb-0 text-2xl">
                            <WidgetName name={widget.name} onUpdate={(name) => metricStore.merge({ name })} />
                        </h1>
                        <div className="text-gray-600">
                            <div
                                onClick={() => setExpanded(!expanded)}
                                className="flex items-center cursor-pointer select-none"
                            >
                                <span className="mr-2 color-teal">{expanded ? 'Collapse' : 'Expand'}</span>
                                <Icon name={expanded ? 'chevron-up' : 'chevron-down'} size="16" color="teal" />
                            </div>
                        </div>
                    </div>

                    { expanded && <WidgetForm onDelete={onBackHandler} {...props}/>}
                </div>

                <WidgetPreview  className="mt-8" />
                <WidgetSessions className="mt-8" />
            </div>
        </Loader>
    ));
}

export default WidgetView;