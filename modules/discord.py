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
    def create_template_embed(self, description):
        _embed = DiscordEmbed(
            title="🚨 UPDATES ARE COMING",
            description=description,
            color=self.embed_color,
        )
        _embed.set_thumbnail(url=self.thumb_url)
        _embed.set_footer(text="Notified by Game Update Notifier")
        _embed.set_timestamp()
        return _embed
    def create_embed_message(self, updated_apps, timestamp):
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

        _embed_fields = []
        _embed_fields.append({'name':"🕑 Checked at", 'value':timestamp.strftime(f"%Y/%m/%d %H:%M:%S")})
        while _apps:
            idx = _apps.rfind("\n", 0, 1024)
            if idx != -1:
                chunk = _apps[:idx + 1]
                _embed_fields.append({'name': "🎮 Updated Games", 'value': chunk})
                _apps = _apps[idx + 1:]
            else:
                chunk = _apps[:1024]
                _embed_fields.append({'name': "🎮 Updated Games", 'value': chunk})
                _apps = _apps[1024:]
        _embeds = []
        chunks = []
        current_chunk = []
        current_char_count = 256 + len("Notified by Game Update Notifier") + len("🚨 UPDATES ARE COMING") + len(_description)
        for field in _embed_fields:
            field_char_count = len(field['name']) + len(field['value'])
            if current_char_count + field_char_count > 6000 or len(current_chunk) == 25:
                chunks.append(current_chunk)
                current_chunk = []
                current_char_count = 256 + len("Notified by Game Update Notifier") + len("🚨 UPDATES ARE COMING") + len(_description)
            current_chunk.append({'name': field['name'], 'value': field['value']})
            current_char_count += field_char_count
        if current_chunk:
            chunks.append(current_chunk)
        for i, chunk in enumerate(chunks):
            _embed = self.create_template_embed(_description)
            for c in chunk:
                _embed.add_embed_field(name=c['name'], value=c['value'], inline=False)
            _embeds.append(_embed)
        return _embeds

    def fire(self, updated_apps, timestamp):
        #self.logger.info("Prepare webhook")
        #_webhook = DiscordWebhook(url=self.webhook_url)

        self.logger.info("Construct embed message(s)")
        _embeds = self.create_embed_message(updated_apps, timestamp)
        #talán 6000 karakter/üzi és nem 6000 karakter/embed ??
        '''for i in range(0, len(_embeds), 10):
            _webhook = DiscordWebhook(url=self.webhook_url)
            for k in range(i, i+10):
                if len(_embeds)<k+1: break
                _webhook.add_embed(_embeds[k])
            _webhook.execute()'''
        for embed in _embeds:
            _webhook = DiscordWebhook(url=self.webhook_url)
            _webhook.add_embed(embed)
            _webhook.execute()