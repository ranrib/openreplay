from chalicelib.core import log_tools
from schemas import schemas

IN_TY = "newrelic"


async def get_all(tenant_id):
    out = await log_tools.get_all_by_tenant(tenant_id=tenant_id, integration=IN_TY)
    return out


async def get(project_id):
    out = await log_tools.get(project_id=project_id, integration=IN_TY)
    return out


async def update(tenant_id, project_id, changes):
    options = {}
    if "region" in changes and len(changes["region"]) == 0:
        options["region"] = "US"
    if "applicationId" in changes:
        options["applicationId"] = changes["applicationId"]
    if "xQueryKey" in changes:
        options["xQueryKey"] = changes["xQueryKey"]

    out = await log_tools.edit(project_id=project_id, integration=IN_TY, changes=options)
    return out


async def add(tenant_id, project_id, application_id, x_query_key, region):
    if region is None or len(region) == 0:
        region = "US"
    options = {"applicationId": application_id, "xQueryKey": x_query_key, "region": region}
    out = await log_tools.add(project_id=project_id, integration=IN_TY, options=options)
    return out


async def delete(tenant_id, project_id):
    out = await log_tools.delete(project_id=project_id, integration=IN_TY)
    return out


async def add_edit(tenant_id, project_id, data: schemas.IntegrationNewrelicSchema):
    s = await get(project_id)
    if s is not None:
        out = await update(tenant_id=tenant_id, project_id=project_id,
                      changes={"applicationId": data.application_id,
                               "xQueryKey": data.x_query_key,
                               "region": data.region})
        return out
    else:
        out = await add(tenant_id=tenant_id,
                   project_id=project_id,
                   application_id=data.application_id,
                   x_query_key=data.x_query_key,
                   region=data.region)
        return out
