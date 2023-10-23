import json

import orpy
import httpx
from decouple import config
from fastapi import HTTPException, status

import schemas
from chalicelib.core import webhook
from chalicelib.core.collaboration_base import BaseCollaboration


class MSTeams(BaseCollaboration):
    @classmethod
    async def add(cls, tenant_id, data: schemas.AddCollaborationSchema):
        nok = await webhook.exists_by_name(tenant_id=tenant_id, name=data.name, exclude_id=None,
                                           webhook_type=schemas.WebhookType.msteams)
        if nok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"name already exists.")
        if cls.say_hello(data.url):
            return webhook.add(tenant_id=tenant_id,
                               endpoint=data.url,
                               webhook_type=schemas.WebhookType.msteams,
                               name=data.name)
        return None

    # https://messagecardplayground.azurewebsites.net
    # https://adaptivecards.io/designer/
    @classmethod
    async def say_hello(cls, url):
        http = orpy.orpy.get().httpx
        r = await http.post(
            url=url,
            json={
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "Hello message",
                "title": "Welcome to OpenReplay"
            })
        if r.status_code != 200:
            print("MSTeams integration failed")
            print(r.text)
            return False
        return True

    @classmethod
    async def send_raw(cls, tenant_id, webhook_id, body):
        http = orpy.orpy.get().httpx
        integration = cls.get_integration(tenant_id=tenant_id, integration_id=webhook_id)
        if integration is None:
            return {"errors": ["msteams integration not found"]}
        try:
            r = await http.post(
                url=integration["endpoint"],
                json=body,
                timeout=5)
            if r.status_code != 200:
                print(f"!! issue sending msteams raw; webhookId:{webhook_id} code:{r.status_code}")
                print(r.text)
                return None
        except httpx.TimeoutException:
            print(f"!! Timeout sending msteams raw webhookId:{webhook_id}")
            return None
        except Exception as e:
            print(f"!! Issue sending msteams raw webhookId:{webhook_id}")
            print(str(e))
            return None
        return {"data": r.text}

    @classmethod
    async def send_batch(cls, tenant_id, webhook_id, attachments):
        http = orpy.orpy.get().httpx
        integration = cls.get_integration(tenant_id=tenant_id, integration_id=webhook_id)
        if integration is None:
            return {"errors": ["msteams integration not found"]}
        print(f"====> sending msteams batch notification: {len(attachments)}")
        for i in range(0, len(attachments), 100):
            print(json.dumps({"type": "message",
                              "attachments": [
                                  {"contentType": "application/vnd.microsoft.card.adaptive",
                                   "contentUrl": None,
                                   "content": {
                                       "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                                       "type": "AdaptiveCard",
                                       "version": "1.2",
                                       "body": attachments[i:i + 100]}}
                              ]}))
            r = await http.post(
                url=integration["endpoint"],
                json={"type": "message",
                      "attachments": [
                          {"contentType": "application/vnd.microsoft.card.adaptive",
                           "contentUrl": None,
                           "content": {
                               "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                               "type": "AdaptiveCard",
                               "version": "1.2",
                               "body": attachments[i:i + 100]}}
                      ]})
            if r.status_code != 200:
                print("!!!! something went wrong")
                print(r)
                print(r.text)

    @classmethod
    async def __share(cls, tenant_id, integration_id, attachement):
        http = orpy.orpy.get().httpx
        integration = cls.get_integration(tenant_id=tenant_id, integration_id=integration_id)
        if integration is None:
            return {"errors": ["Microsoft Teams integration not found"]}
        r = await http.post(
            url=integration["endpoint"],
            json={"type": "message",
                  "attachments": [
                      {"contentType": "application/vnd.microsoft.card.adaptive",
                       "contentUrl": None,
                       "content": {
                           "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                           "type": "AdaptiveCard",
                           "version": "1.5",
                           "body": [attachement]}}
                  ]
                  })

        return r.text

    @classmethod
    async def share_session(cls, tenant_id, project_id, session_id, user, comment, integration_id=None):
        title = f"[{user}](mailto:{user}) has shared the below session!"
        link = f"{config('SITE_URL')}/{project_id}/session/{session_id}"
        link = f"[{link}]({link})"
        args = {"type": "ColumnSet",
                "style": "emphasis",
                "separator": True,
                "bleed": True,
                "columns": [{
                    "width": "stretch",
                    "items": [
                        {"type": "TextBlock",
                         "text": title,
                         "style": "heading",
                         "size": "Large"},
                        {"type": "TextBlock",
                         "spacing": "small",
                         "text": link}
                    ]
                }]}
        if comment and len(comment) > 0:
            args["columns"][0]["items"].append({
                "type": "TextBlock",
                "spacing": "small",
                "text": comment
            })
        data = await cls.__share(tenant_id, integration_id, attachement=args)
        if "errors" in data:
            return data
        return {"data": data}

    @classmethod
    async def share_error(cls, tenant_id, project_id, error_id, user, comment, integration_id=None):
        title = f"[{user}](mailto:{user}) has shared the below error!"
        link = f"{config('SITE_URL')}/{project_id}/errors/{error_id}"
        link = f"[{link}]({link})"
        args = {"type": "ColumnSet",
                "style": "emphasis",
                "separator": True,
                "bleed": True,
                "columns": [{
                    "width": "stretch",
                    "items": [
                        {"type": "TextBlock",
                         "text": title,
                         "style": "heading",
                         "size": "Large"},
                        {"type": "TextBlock",
                         "spacing": "small",
                         "text": link}
                    ]
                }]}
        if comment and len(comment) > 0:
            args["columns"][0]["items"].append({
                "type": "TextBlock",
                "spacing": "small",
                "text": comment
            })
        data = await cls.__share(tenant_id, integration_id, attachement=args)
        if "errors" in data:
            return data
        return {"data": data}

    @classmethod
    def get_integration(cls, tenant_id, integration_id=None):
        if integration_id is not None:
            out = await webhook.get_webhook(tenant_id=tenant_id, webhook_id=integration_id,
                                       webhook_type=schemas.WebhookType.msteams)
            return out

        integrations = await webhook.get_by_type(tenant_id=tenant_id, webhook_type=schemas.WebhookType.msteams)
        if integrations is None or len(integrations) == 0:
            return None
        return integrations[0]
