import discord.ext.commands as commands
import mcrcon
import json

config = {}
try:
	config = json.load(open("config.json", "r"))
except FileNotFoundError:
	print("Please create a config.json with the following layout:")
	exit(1)

wlist = "whitelisted.json"
bot = commands.Bot(command_prefix=config["prefix"])


def send_rcon(msg):
	with mcrcon.MCRcon(config["mc_server"], config["rcon_pass"]) as r:
		return r.command(msg)


def is_acct_whitelisted(acct):
	try:
		with open(wlist, "r") as file:
			j = json.load(file)
			if acct in j.values():
				return True
			return False
	except FileNotFoundError:
		# Create empty json
		with open(wlist, "w") as file:
			file.write("{}")
			file.close()
		return False
	except Exception as e:
		print(e)
		exit(1)


def get_old_acct(userid):
	with open(wlist, "r") as file:
		j = json.load(file)
		uid = str(userid)
		if uid in j:
			return j[uid]
		else:
			return ""


def add_whitelist(userid, acct):
	with open(wlist, "r") as file:
		j = json.load(file)
		j[str(userid)] = acct
	with open(wlist, "w") as file:
		json.dump(j, file)
	return send_rcon(f"/whitelist add {acct}")


def remove_whitelist(userid, acct):
	with open(wlist, "r") as file:
		j = json.load(file)
		del j[str(userid)]
	with open(wlist, "w") as file:
		json.dump(j, file)
	return send_rcon(f"/whitelist remove {acct}")


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	await bot.process_commands(message)


@bot.command(name="whitelist")
async def whitelist(ctx, arg):
	print(arg)
	# First check if the username is already whitelisted.
	if is_acct_whitelisted(arg):
		await ctx.send(f"{arg} is already whitelisted")
	else:
		# If this user already has an account whitelisted, remove it.
		old_acct = get_old_acct(ctx.author.id)
		if old_acct != "":
			msg = remove_whitelist(ctx.author.id, old_acct)
			await ctx.send(msg)
		# And whitelist the new account
		msg = add_whitelist(ctx.author.id, arg)
		await ctx.send(msg)


@whitelist.error
async def whitelist_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Usage: !whitelist username")


@bot.command(name="get_whitelist")
async def get_whitelist(ctx):
	await ctx.send(send_rcon("/whitelist list"))


@bot.command(name="playing")
async def playing(ctx):
	await ctx.send(send_rcon("/list"))


def main():
	bot.run(config["token"])


if __name__ == "__main__":
	main()
