import discord

class PageViewer(discord.ui.View):
    def __init__(self,current_page,embed_list):
        super().__init__()
        self.current_page = current_page
        self.embed = embed_list[current_page]
        self.embed_list = embed_list


    @discord.ui.button(emoji="<:first:910500659621691452>",style=discord.ButtonStyle.primary)
    async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = 0
        await interaction.response.edit_message(embed=self.embed_list[self.current_page])

    @discord.ui.button(emoji="<:previous:910500672376561664>",style=discord.ButtonStyle.gray)
    async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page -= 1
        if self.current_page >= len(self.embed_list) or self.current_page < 0:
            self.current_page = 0
        await interaction.response.edit_message(embed=self.embed_list[self.current_page])

    @discord.ui.button(emoji="<:bluearrow:910500655548989491>",style=discord.ButtonStyle.gray)
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1
        if self.current_page >= len(self.embed_list):
            self.current_page = 0
        await interaction.response.edit_message(embed=self.embed_list[self.current_page])

    @discord.ui.button(emoji="<:last:910500662071160912>",style=discord.ButtonStyle.primary)
    async def last(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = len(self.embed_list) - 1
        await interaction.response.edit_message(embed=self.embed_list[self.current_page])
