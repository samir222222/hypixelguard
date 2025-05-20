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
            guild = discord.Object(id=895840135013343344)
            synced = await self.tree.sync(guild=guild)
            print(f"synced {len(synced)} commands to guild {guild.id}")
        except Exception as e:
            print(f"error syncing commands {e}")

    async def on_message(self, message):
        print(f"{message.author} : {message.content}")
        if message.author == self.user:
            return

        if message.content.startswith('hello'):
            await message.reply(f'hello {message.author.mention}')
        await self.process_commands(message)

intents = discord.Intents.all()

client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=895840135013343344)

@client.tree.command(name="hello", description="say hello!", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there")

@client.tree.command(name="bye", description="say bye!", guild=GUILD_ID)
async def sayBye(interaction: discord.Interaction, print_name: str):
    await interaction.response.send_message(f"bye bye {print_name}")

@client.tree.command(name="embed", description="makes an embed!", guild=GUILD_ID)
async def makeemb(interaction: discord.Interaction):
    embed = discord.Embed(title="this is the title", description="this is the description", url="https://www.google.com/", color=discord.Color.blue())
    embed.set_thumbnail(url="https://i.pinimg.com/736x/b7/ea/e2/b7eae22df79bf7243e3801ff07843f6e.jpg")
    embed.add_field(name="field 1 title", value="this is the value of the first field", inline=False)
    embed.add_field(name="field 2 title", value="this is the value of the second field")
    embed.set_footer(text="this is the footer text", icon_url="https://i.pinimg.com/736x/b7/ea/e2/b7eae22df79bf7243e3801ff07843f6e.jpg")
    embed.set_author(name=interaction.user.name)
    await interaction.response.send_message(embed=embed)

class View2(discord.ui.View):
    @discord.ui.button(label="Click me", style=discord.ButtonStyle.blurple, emoji="🔥")
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("you clicked the blurple button")

    @discord.ui.button(label="Don't click me", style=discord.ButtonStyle.danger, emoji="🥵")
    async def button_callback2(self, button, interaction):
        await interaction.response.send_message("you clicked the red button")

    @discord.ui.button(label="im the best button!", style=discord.ButtonStyle.success, emoji="😀")
    async def button_callback3(self, button, interaction):
        await interaction.response.send_message("you clicked the green button")

@client.tree.command(name="button", description="say button!", guild=GUILD_ID)
async def saybutton(interaction: discord.Interaction):
    await interaction.response.send_message(view=View2())


@client.tree.command(name="strike", description="Adds a strike to a server member", guild=GUILD_ID)
async def strike(interaction: discord.Interaction, member: discord.Member, message: str): 
    guild_id = interaction.guild.id

    try:
        connection = mysql.connector.connect(host="localhost", database="hypixelguard", user="root", password="root")
        cursor = connection.cursor()

        # Check if table exists, create if not
        cursor.execute(f"SHOW TABLES LIKE 'DB_{guild_id}'")
        result = cursor.fetchone()
        if not result:
            Mysql_Create_table_Query = f"""CREATE TABLE DB_{guild_id} (
                                        id INT(11) NOT NULL AUTO_INCREMENT,
                                        User VARCHAR(250) NOT NULL,
                                        Message VARCHAR(5000) NOT NULL,
                                        Number of strikes VARCHAR(5000) NOT NULL,
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


@client.tree.command(name="strikelist", description="shows the list of strikes", guild=GUILD_ID)
async def strikelist(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    try:
        embed = discord.Embed(title="Strike List", description="List of members and their strikes", color=discord.Color.orange())
        connection = mysql.connector.connect(host="localhost", database="hypixelguard", user="root", password="root")
        cursor = connection.cursor()
        mysql_strikelist = f"SELECT User, `Number_of_strikes`, Message FROM DB_{guild_id}"
        cursor.execute(mysql_strikelist)
        results = cursor.fetchall()

        if results:
            for row in results:
                user, strikes, messages = row
                embed.add_field(name=user, value=f"Strikes: {strikes}\nMessages: {messages[:3000]}", inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No strikes have been recorded yet.")

    except mysql.connector.Error as error:
        print(f"failed to show the strike list: {error}")
        await interaction.response.send_message(f"An error occurred while showing the strike list: {error}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()






















            

client.run('MTM1NDUzMzU4NDQwODQxNjM5OA.GFqHWR.m90c9E_4kvE_Hjco10eCmXU1SohXVcrAVg8G_Q')