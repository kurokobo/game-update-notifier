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

    def create_embed_message(self, updated_apps, timestamp):

        _mention = ""
        for _role_id in self.role_ids:
            _mention += "<@&{}> ".format(_role_id)
        for _user_id in self.user_ids:
            _mention += "<@{}> ".format(_user_id)

        _description = "{}\n".format(_mention)
        _description += "Updates have been detected on {}".format(self.platform)

        _embed = DiscordEmbed(
            title="🚨 UPDATES ARE COMING",
            description=_description,
            color=self.embed_color,
        )

        _apps = ""
        for _updated_app in updated_apps:
            _apps += "💡 **{}** ({})\n".format(
                _updated_app.name,
                _updated_app.id,
            )

        _embed.set_thumbnail(url=self.thumb_url)
        _embed.add_embed_field(name="🎮 Updated Games", value=_apps)
        _embed.add_embed_field(
            name="🕑 Checked at", value=timestamp.strftime("%Y/%m/%d %H:%M:%S")
        )
        _embed.set_footer(text="Notified by Game Update Notifier")
        _embed.set_timestamp()

        return _embed

    def fire(self, updated_apps, timestamp):
        self.logger.info("Prepare webhook")
        _webhook = DiscordWebhook(url=self.webhook_url)

        self.logger.info("Construct embed message")
        _embed = self.create_embed_message(updated_apps, timestamp)

        self.logger.info("Post embed message")
        _webhook.add_embed(_embed)
        _webhook.execute()
