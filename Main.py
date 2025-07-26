import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from mysql.connector import Error
from keep_alive import keep_alive

keep_alive()

class Client(commands.Bot):
    async def on_ready(self):
        print(f"logged on as {self.user}")
        try:
            guild = discord.Object(id=650800280731910205)
            synced = await self.tree.sync(guild=guild)
            print(f"synced {len(synced)} commands to guild {guild.id}")
        except Exception as e:
            print(f"error syncing commands {e}")


intents = discord.Intents.all()

client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=650800280731910205)



@client.tree.command(name="strike", description="Adds a strike to a server member", guild=GUILD_ID)
async def strike(interaction: discord.Interaction, member: discord.Member, message: str): 
    guild_id = interaction.guild.id

    try:
        connection = mysql.connector.connect(host="localhost", database="hypixelguard", user="root", password="root")
        cursor = connection.cursor()

        
        cursor.execute(f"SHOW TABLES LIKE 'DB_{guild_id}'")
        result = cursor.fetchone()
        if not result:
            Mysql_Create_table_Query = f"""CREATE TABLE DB_{guild_id} (
                                        id INT(11) NOT NULL AUTO_INCREMENT,
                                        User VARCHAR(250) NOT NULL,
                                        Message VARCHAR(5000) NOT NULL,
                                        Number_of_strikes VARCHAR(5000) DEFAULT 1,
                                        PRIMARY KEY (id))"""
            cursor.execute(Mysql_Create_table_Query)
            print(f"Guild {guild_id} table created successfully")

        table = f"DB_{guild_id}"
        cursor.execute(f"SELECT * FROM DB_{guild_id} WHERE User LIKE '{member}'")
        result2 = cursor.fetchone()
        if not result2:
            mySql_Insert_ROw_Query = f"INSERT INTO {table} (User, Message) VALUES (%s, %s)"
            mySql_Insert_ROw_values = (str(member), message)
            cursor.execute(mySql_Insert_ROw_Query, mySql_Insert_ROw_values)
        else:
            mySql_update_ROw_Query = f"UPDATE DB_{guild_id} SET Number_of_strikes = Number_of_strikes + 1 , Message = CONCAT(Message,',''{message}') WHERE User = '{member}'"
            cursor.execute(mySql_update_ROw_Query)
        connection.commit()
        mysql_number_of_strikes = f"SELECT Number_of_strikes FROM DB_{guild_id} WHERE User = '{member}'"
        cursor.execute(mysql_number_of_strikes)
        result3 = cursor.fetchall()
        await interaction.response.send_message(f"Strike added for {member.mention}, they now have: {result3} strikes")

    except mysql.connector.Error as error:
        print(f"failed to create table or insert data in MYSQL: {error}")
        await interaction.response.send_message(f"An error occurred while adding the strike: {error}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


 
class StrikeListView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, all_strikes: list, page_start: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.original_interaction = interaction
        self.all_strikes = all_strikes
        self.page_start = page_start
        self.strikes_per_page = 10

    def create_embed(self):
        embed = discord.Embed(title="Strike List", description="List of members and their strikes", color=discord.Color.orange())
        end = min(self.page_start + self.strikes_per_page, len(self.all_strikes))
        if self.all_strikes:
            for row in self.all_strikes[self.page_start:end]:
                user, strikes, messages = row
                embed.add_field(name=user, value=f"Strikes: {strikes}\nMessages: {messages[:3000]}", inline=False)
        else:
            embed.description = "No strikes have been recorded yet."
        return embed

    @discord.ui.button(label="Next 10", style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_page(self,interaction: discord.Interaction,button: discord.ui.Button):
        self.page_start += self.strikes_per_page
        if self.page_start >= len(self.all_strikes):
            self.page_start = 0  
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

@client.tree.command(name="strikelist", description="shows the list of strikes", guild=GUILD_ID)
async def strikelist(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    try:
        connection = mysql.connector.connect(host="localhost", database="hypixelguard", user="root", password="root")
        cursor = connection.cursor()
        mysql_strikelist = f"SELECT User, `Number_of_strikes`, Message FROM DB_{guild_id}"
        cursor.execute(mysql_strikelist)
        results = cursor.fetchall()

        if results:
            view = StrikeListView(interaction, results)
            await interaction.response.send_message(embed=view.create_embed(), view=view)
        else:
            await interaction.response.send_message("No strikes have been recorded yet.")

    except mysql.connector.Error as error:
        print(f"failed to show the strike list: {error}")
        await interaction.response.send_message(f"An error occurred while showing the strike list: {error}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()



@client.tree.command(name="strikeremove", description="removes a strike from a member", guild=GUILD_ID)
async def removestrike(interaction: discord.Interaction, member: discord.Member): 
    guild_id = interaction.guild.id

    try:
        connection = mysql.connector.connect(host="localhost", database="hypixelguard", user="root", password="root")
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM DB_{guild_id} WHERE User LIKE '{member}'")
        result4 = cursor.fetchall()
        if result4:
            MySQL_Qwery_update1 = f"UPDATE DB_{guild_id} SET Number_of_strikes = Number_of_strikes - 1 WHERE User = '{member}'"
            cursor.execute(MySQL_Qwery_update1)
            mysql_row_remove = f"DELETE FROM DB_{guild_id} WHERE Number_of_strikes = 0"
            cursor.execute(mysql_row_remove)
        connection.commit()
        mysql_number_of_strikes = f"SELECT Number_of_strikes FROM DB_{guild_id} WHERE User = '{member}'"
        cursor.execute(mysql_number_of_strikes)
        result5 = cursor.fetchall()
        await interaction.response.send_message(f"Strike removed from {member.mention}, they now have: {result5} strikes")

    except mysql.connector.Error as error:
        print(f"failed to create table or insert data in MYSQL: {error}")
        await interaction.response.send_message(f"An error occurred while removing the strike: {error}")


    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()






            

client.run('MTM1NDUzMzU4NDQwODQxNjM5OA.GFqHWR.m90c9E_4kvE_Hjco10eCmXU1SohXVcrAVg8G_Q')



