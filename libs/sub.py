from telethon.tl.functions.channels import JoinChannelRequest


class CheckSubscribe:
    def __init__(self, client, channel_name="vsecoder_m"):
        super().__init__()
        self.channel_name = channel_name
        self.client = client
        self.is_sub = self.check()
        
    def check(self):
        try:
            channel = await self.client.get_entity(f"t.me/{self.channel_name}")
            if channel.title:
                return True
            return False
        except Exception:
            return False
