from __future__ import annotations

from typing import List, Union, Iterable, Tuple

import discord

from redbot.core.i18n import Translator
from redbot.core.utils.chat_formatting import humanize_number, escape
from redbot.core.utils._dpy_menus_utils import SimpleHybridMenu
from redbot.vendored.discord.ext import menus

_ = Translator("CustomCommands", __file__)


class CCListSource(menus.ListPageSource):
    def __init__(self, custom_commands: Iterable[Tuple[str, dict]]):
        super().__init__(custom_commands, per_page=5)

    async def format_page(
        self, menu: SimpleHybridMenu, entries: Iterable[Tuple[str, dict]]
    ) -> Union[discord.Embed, str]:
        current_entry = menu.current_page + 1
        total_entries = self._max_pages

        results = []
        for command, body in entries:
            responses = body["response"]

            if isinstance(responses, list):
                result = ", ".join(map(discord.utils.escape_markdown, responses))
            elif isinstance(responses, str):
                result = discord.utils.escape_markdown(responses)
            else:
                continue
            # Cut preview to 52 characters max
            if len(result) > 52:
                result = result[:49] + "..."
            # Replace newlines with spaces
            result = result.replace("\n", " ")
            # Escape markdown and mass mentions
            result = escape(result, formatting=True, mass_mentions=True)
            results.append((f"{menu.ctx.clean_prefix}{command}", result))

        if await menu.ctx.embed_requested():
            # We need a space before the newline incase the CC preview ends in link (GH-2295)
            content = " \n".join(map("**{0[0]}** : {0[1]}".format, results))
            embed = discord.Embed(
                title=_("Custom Command List"),
                description=content,
                colour=await menu.ctx.embed_colour(),
            )
            if total_entries > 1:
                text = _("Page: {page_num}/{total_pages}\n").format(
                    page_num=humanize_number(current_entry),
                    total_pages=humanize_number(max(1, total_entries)),
                )
                embed.set_footer(text=text)
            return embed
        else:
            return "\n".join(map("{0[0]:<12} : {0[1]}".format, results))


class CCRawSource(menus.ListPageSource):
    def __init__(self, custom_commands: List[str]):
        super().__init__(custom_commands, per_page=1)

    async def format_page(self, menu: SimpleHybridMenu, entry: str) -> Union[discord.Embed, str]:
        raw = discord.utils.escape_markdown(entry)
        current_entry = menu.current_page + 1
        total_entries = self._max_pages
        if await menu.ctx.embed_requested():
            colour = await menu.ctx.embed_colour()
            if len(raw) > 2048:
                raw = f"{raw[:2045]}..."
            embed = discord.Embed(
                title=_("Response #{num}").format(num=current_entry),
                description=raw,
                colour=colour,
            )
            if total_entries > 1:
                text = _("Page: {page_num}/{total_pages}\n").format(
                    page_num=humanize_number(current_entry),
                    total_pages=humanize_number(max(1, total_entries)),
                )
                embed.set_footer(text=text)
            return embed
        else:
            msg = _("Response #{num}/{total}:\n{raw}").format(
                num=humanize_number(current_entry),
                total=humanize_number(max(1, total_entries)),
                raw=raw,
            )
            if len(msg) > 2000:
                msg = f"{msg[:1997]}..."
            return msg
