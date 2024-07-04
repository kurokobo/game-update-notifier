import logging

from discord_webhook import DiscordEmbed, DiscordWebhook


class Discord:
    def __init__(
        self, webhook_url, role_ids, user_ids, platform, thumb_url, embed_color
    ):
        self.logger = logging.getLogger(__name__)
        self.platform = platform
        self.webhook_url = webhook_url
        self.role_ids = role_ids
        self.user_ids = user_ids
        self.thumb_url = thumb_url
        self.embed_color = embed_color
    def create_embed(self, description, timestamp, chunk):
        _embed = DiscordEmbed(
            title="🚨 UPDATES ARE COMING",
            description=description,
            color=self.embed_color,
        )
        _embed.set_thumbnail(url=self.thumb_url)
        _embed.add_embed_field(name="🎮 Updated Games", value=chunk)
        _embed.add_embed_field(
            name="🕑 Checked at", value=timestamp.strftime(f"%Y/%m/%d %H:%M:%S")
        )
        _embed.set_footer(text="Notified by Game Update Notifier")
        _embed.set_timestamp()
        return _embed
    def create_embed_messages(self, updated_apps, timestamp):

        _mention = ""
        for _role_id in self.role_ids:
            _mention += "<@&{}> ".format(_role_id)
        for _user_id in self.user_ids:
            _mention += "<@{}> ".format(_user_id)

        _description = "{}\n".format(_mention)
        _description += "Updates have been detected on {}".format(self.platform)

        _apps = ""
        for _updated_app in updated_apps:
            _apps += "💡 **{}** ({})\n".format(
                _updated_app.name,
                _updated_app.id,
            )
        _embeds = []
        while _apps:
            idx = _apps.rfind("\n", 0, 1024)
            if idx != -1:
                chunk = _apps[:idx + 1]
                _embed = self.create_embed(_description, timestamp, chunk)
                _embeds.append(_embed)
                _apps = _apps[idx + 1:]
            else:
                chunk = _apps[:1024]
                _embed = self.create_embed(_description, timestamp, chunk)
                _embeds.append(_embed)
                _apps = _apps[1024:]    
        return _embeds

    def fire(self, updated_apps, timestamp):
        self.logger.info("Prepare webhook")
        _webhook = DiscordWebhook(url=self.webhook_url)

        self.logger.info("Construct embed message(s)")
        _embeds = self.create_embed_messages(updated_apps, timestamp)
        for _embed in _embeds:
            self.logger.info("Post embed message")
            _webhook.add_embed(_embed)
            _webhook.execute()
