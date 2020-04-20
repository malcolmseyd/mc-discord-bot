import discord.ext.commands
import mcrcon
import json

config = {}
try:
	config = json.load(open("config.json", "r"))
except FileNotFoundError:
	print("Please create a config.json with the following layout:")
	exit(1)

bot = discord.ext.commands.Bot(command_prefix=config["prefix"])


def is_acct_whitelisted(acct):
	try:
		with open("whitelisted.txt", "r") as file:
			for line in file:
				old_acct = line.split(":")[1].strip()
				if old_acct == acct:
					return True
			return False
	except FileNotFoundError:
		with open("whitelisted.txt", "w+") as file:
			file.close()
		return False


def get_old_acct(userid):
	with open("whitelisted.txt", "r") as file:
		for line in file:
			if line.split(":")[0] == str(userid):
				return line.split(":")[1].strip()
		return ""


def already_whitelisted(acct):
	try:
		with open("whitelisted.txt", "r") as file:
			for line in file:
				old_acct = line.split(":")[1].strip()
				# Handle either username (given argument)
				if type(acct) is str:
					if old_acct == acct:
						return old_acct
				# Or user id (from discord)
				elif type(acct) is int:
					if line.split(":")[0] == str(acct):
						return old_acct
			return ""
	except FileNotFoundError:
		with open("whitelisted.txt", "w+") as file:
			file.close()
		return ""


def add_whitelist(userid, acct):
	with mcrcon.MCRcon(config["mc_server"], config["rcon_pass"]) as r:
		cmd = f"/whitelist add {acct}"
		message = r.command(cmd)
	with open("whitelisted.txt", "a") as f:
		f.write(f"{userid}:{acct}\n")
	return message


def remove_whitelist(userid, acct):
	with mcrcon.MCRcon(config["mc_server"], config["rcon_pass"]) as r:
		cmd = f"/whitelist remove {acct}"
		message = r.command(cmd)
	with open("whitelisted.txt", "r") as file:
		lines = file.readlines()
	with open("whitelisted.txt", "w") as file:
		for line in lines:
			if str(userid) not in line:
				file.write(line)
	return message


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	await bot.process_commands(message)


@bot.command(name="whitelist")
async def whitelist(ctx, arg):
	# First check if the username is already whitelisted.
	# old_acct = already_whitelisted(arg)
	# if old_acct == arg:
	if is_acct_whitelisted(arg):
		await ctx.send(f"{arg} is already whitelisted")
	else:
		# If this user already has an account whitelisted, remove it.
		old_acct = get_old_acct(ctx.author.id)
		if old_acct != "":
			await ctx.send(remove_whitelist(ctx.author.id, old_acct))
		# And whitelist the new account
		await ctx.send(add_whitelist(ctx.author.id, arg))


@bot.command(name="get_whitelist")
async def get_whitelist(ctx):
	with mcrcon.MCRcon(config["mc_server"], config["rcon_pass"]) as r:
		await ctx.send(r.command(f"/whitelist list"))


def main():
	bot.run(config["token"])


if __name__ == "__main__":
	main()
