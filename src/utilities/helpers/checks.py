from discord.ext import commands
from typing import Dict, Any

DEFAULT: Dict[str, Any] = {
    "guild_id": None,
    "logs": {
        "message_delete": None,
        "message_edit": None,
        "member_join": None,
        "member_remove": None,
        "member_ban": None,
        "member_unban": None,
        "vc_state_change": None,
        "channel_create": None,
        "channel_delete": None,
        "role_create": None,
        "role_delete": None,
    },
    "modlog": {
        "member_warn": None,
        "member_mute": None,
        "member_unmute": None,
        "member_kick": None,
        "member_ban": None,
        "member_unban": None,
        "member_mute": None,
        "member_softban": None,
        "message_purge": None,
        "channel_lockdown": None,
        "channel_slowmode": None,
    },
    "time_offset": 0,
    "detections": {
        "filters": [],
        "regex_filters": [],
        "image_filters": [],
        "block_invite": False,
        "english_only": False,
        "mention_limit": None,
        "spam_detection": None,
        "repetitive_message": None,
        "repetitive_characters": None,
        "max_lines": None,
        "max_words": None,
        "max_characters": None,
        "sexually_explicit": [],
        "caps_message_percent": None,
        "caps_message_min_words": None,
    },
    "detection_punishments": {
        "filters": {
            "warn": 1,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "regex_filters": {
            "warn": 1,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "image_filters": {
            "warn": 1,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "block_invite": {
            "warn": 1,
            "mute": "10 minutes",
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "english_only": {
            "warn": 0,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "mention_limit": {
            "warn": 1,
            "mute": "10 minutes",
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "spam_detection": {
            "warn": 1,
            "mute": "10 minutes",
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "repetitive_message": {
            "warn": 1,
            "mute": "10 minutes",
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "repetitive_characters": {
            "warn": 0,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "max_lines": {
            "warn": 0,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "max_words": {
            "warn": 0,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "max_characters": {
            "warn": 0,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "sexually_explicit": {
            "warn": 1,
            "mute": "10 minutes",
            "kick": False,
            "ban": False,
            "delete": True,
        },
        "caps_message": {
            "warn": 0,
            "mute": None,
            "kick": False,
            "ban": False,
            "delete": True,
        },
    },
    "alert": {
        "kick": None,
        "ban": None,
        "softban": None,
        "mute": None,
        "unmute": None,
    },
    "giveaway": {
        "channel_id": None,
        "role_id": None,
        "emoji_id": None,
        "message_id": None,
        "ended": False,
    },
    "perm_levels": [],
    "command_levels": [],
    "warn_punishments": [],
    "notes": [],
    "warns": [],
    "mutes": [],
    "tags": [],
    "whitelisted_guilds": [],
    "reaction_roles": [],
    "selfroles": [],
    "autoroles": [],
    "ignored_channels": {
        "filters": [],
        "regex_filters": [],
        "image_filters": [],
        "block_invite": [],
        "english_only": [],
        "mention_limit": [],
        "spam_detection": [],
        "repetitive_message": [],
        "repetitive_characters": [],
        "max_lines": [],
        "max_words": [],
        "max_characters": [],
        "sexually_explicit": [],
        "caps_message": [],
        "message_delete": [],
        "message_edit": [],
        "channel_delete": [],
    },
    "events_announce": {"member_join": {}, "member_remove": {}},
    "canned_variables": {},
    "ignored_channels_in_prod": [],
    "mute_role": None,
    "prefix": "!!",
}


def check_permissions(ctx, perms):

    ch = ctx.message.channel
    author = ctx.message.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


def is_gowner(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        guild = ctx.guild
        owner = guild.owner

        if ctx.message.author.id == owner.id:
            return True

        return check_permissions(ctx, perms)

    return commands.check(predicate)


def can_mute(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.mute_members:
            return True
        else:
            return False

    return commands.check(predicate)


def can_kick(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.kick_members:
            return True
        else:
            return False

    return commands.check(predicate)


def can_ban(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.ban_members:
            return True
        else:
            return False

    return commands.check(predicate)


def can_managemsg(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.manage_messages:
            return True
        else:
            return False

    return commands.check(predicate)


def can_manageguild(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.manage_guild:
            return True
        else:
            return False

    return commands.check(predicate)


def is_admin(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.administrator:
            return True
        else:
            return False

    return commands.check(predicate)
