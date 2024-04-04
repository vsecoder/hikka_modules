
class CheckSubscribe:
    def __init__(self):
        super().__init__()

    async def check(self, client, channel_name="vsecoder_m"):
        try:
            channel = await client.get_entity(f"t.me/{channel_name}")
            if channel.title:
                return True
            return False
        except Exception:
            return False
