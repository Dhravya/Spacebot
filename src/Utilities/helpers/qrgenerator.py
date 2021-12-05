import discord
import re
from typing import Callable, ClassVar, List, Optional, Pattern, Sequence, Tuple, Union, cast
from discord.ext import commands
class MessagePredicate(Callable[[discord.Message], bool]):

    def __init__(self, predicate: Callable[["MessagePredicate", discord.Message], bool]) -> None:
        self._pred: Callable[["MessagePredicate", discord.Message], bool] = predicate
        self.result = None

    def __call__(self, message: discord.Message) -> bool:
        return self._pred(self, message)

    @classmethod
    def contained_in(
        cls,
        collection: Sequence[str],
        ctx: Optional[commands.Context] = None,
        channel: Optional[Union[discord.TextChannel, discord.DMChannel]] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        """Match if the response is contained in the specified collection.
        The index of the response in the ``collection`` sequence is
        assigned to the `result` attribute.
        Parameters
        ----------
        collection : Sequence[str]
            The collection containing valid responses.
        ctx : Optional[Context]
            Same as ``ctx`` in :meth:`same_context`.
        channel : Optional[discord.TextChannel]
            Same as ``channel`` in :meth:`same_context`.
        user : Optional[discord.abc.User]
            Same as ``user`` in :meth:`same_context`.
        Returns
        -------
        MessagePredicate
            The event predicate.
        """
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            try:
                self.result = collection.index(m.content)
            except ValueError:
                return False
            else:
                return True

        return cls(predicate)

    @classmethod
    def same_context(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[Union[discord.TextChannel, discord.DMChannel]] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        """Match if the message fits the described context.
        Parameters
        ----------
        ctx : Optional[Context]
            The current invocation context.
        channel : Optional[discord.TextChannel]
            The channel we expect a message in. If unspecified,
            defaults to ``ctx.channel``. If ``ctx`` is unspecified
            too, the message's channel will be ignored.
        user : Optional[discord.abc.User]
            The user we expect a message from. If unspecified,
            defaults to ``ctx.author``. If ``ctx`` is unspecified
            too, the message's author will be ignored.
        Returns
        -------
        MessagePredicate
            The event predicate.
        """
        if ctx is not None:
            channel = channel or ctx.channel
            user = user or ctx.author

        return cls(
            lambda self, m: (user is None or user.id == m.author.id)
            and (channel is None or channel.id == m.channel.id)
        )

    @classmethod
    def cancelled(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[Union[discord.TextChannel, discord.DMChannel]] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        """Match if the message is ``[p]cancel``.
        Parameters
        ----------
        ctx : Optional[Context]
            Same as ``ctx`` in :meth:`same_context`.
        channel : Optional[discord.TextChannel]
            Same as ``channel`` in :meth:`same_context`.
        user : Optional[discord.abc.User]
            Same as ``user`` in :meth:`same_context`.
        Returns
        -------
        MessagePredicate
            The event predicate.
        """
        same_context = cls.same_context(ctx, channel, user)
        return cls(
            lambda self, m: (same_context(m) and m.content.lower() == f"{ctx.prefix}cancel")
        )