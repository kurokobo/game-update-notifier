import logging

from discord_webhook import DiscordEmbed, DiscordWebhook

logger = logging.getLogger(__name__)


def create_embed_message(user_id, app_name, app_id, branch, latest):
    desc = (
        "<@!{}>\n".format(user_id)
        + "{} seems to be updated on {} branch.\n".format(app_name, branch)
        + "Now it's time to dive into the RAM and find new offsets."
    )
    embed = DiscordEmbed(
        title="🚨🚨🚨 {} IS UPDATED 🚨🚨🚨".format(app_name.upper()),
        description=desc,
        color="03b2f8",
    )
    embed.add_embed_field(name="Updated Time", value=latest)
    embed.add_embed_field(
        name="App Info", value="{} ({}) @ {}".format(app_name, app_id, branch)
    )
    embed.set_footer(text="Notified by Steam Update Notifier")
    embed.set_timestamp()
    return embed


def Fire(webhook_url, user_id, app_name, app_id, branch, message):
    logger.info("Prepare webhook")
    webhook = DiscordWebhook(url=webhook_url)

    logger.info("Construct embed message")
    embed = create_embed_message(user_id, app_name, app_id, branch, message)

    logger.info("Post embed message")
    webhook.add_embed(embed)
    webhook.execute()
