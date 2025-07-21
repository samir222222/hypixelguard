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
