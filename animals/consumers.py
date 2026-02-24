import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AdoptionRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated:
            self.group_name = f"user_requests_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def adoption_status_update(self, event):
        html_content = event["html"]
        
        await self.send(text_data=json.dumps({
            "html": html_content
        }))
