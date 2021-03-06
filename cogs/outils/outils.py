import asyncio
import datetime
import operator
import os
import random
import re
import time
from urllib import request

import discord
from __main__ import send_cmd_help
from discord.ext import commands

from .utils import checks
from .utils.dataIO import fileIO, dataIO


class Outils:
    """Module d'outils utiles à la modération ou aux statistiques"""
    def __init__(self, bot):
        self.bot = bot
        self.results = dataIO.load_json("data/outils/results.json")

    @commands.command(aliases=["ss"], pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def superstats(self, ctx, max:int, channelid, nom:str):
        """Récolte des statistiques sur tous les messages d'un channel
        Prend en compte les messages, mots et lettres + premier message de chaque membre
        Un nom doit être donné afin d'enregistrer les données en JSON"""
        await self.bot.say("Début de l'analyse...")
        channel = self.bot.get_channel(channelid)
        nom = nom.lower()
        if nom in self.results:
            await self.bot.say("Nom déjà existant pour enregistrement")
            return
        data = {}
        n = 0
        async for msg in self.bot.logs_from(channel, limit=max):
            if n == (0.25 * max):
                await self.bot.say("**Analyse** | Env. 25%")
            if n == (0.50 * max):
                await self.bot.say("**Analyse** | Env. 50%")
            if n == (0.75 * max):
                await self.bot.say("**Analyse** | Env. 75%")
            if n == (0.90 * max):
                await self.bot.say("**Analyse** | Env. 90%")
            n += 1
            ts = msg.timestamp
            mots = len(msg.content.split(" "))
            lettres = len(msg.content)
            user = msg.author
            if user.id not in data:
                data[user.id] = {"OLDEST_MSG": ts,
                                 "PSEUDO": user.name,
                                 "T_MSG": 0,
                                 "T_MOTS": 0,
                                 "T_LETTRES": 0}
            if data[user.id]["OLDEST_MSG"] > ts: data[user.id]["OLDEST_MSG"] = ts
            data[user.id]["T_MSG"] += 1
            data[user.id]["T_MOTS"] += mots
            data[user.id]["T_LETTRES"] += lettres
        txt = ""
        for e in data:
            txt += "{}\t{}\t{}\t{}\n".format(data[e]["PSEUDO"],
                                             data[e]["T_MSG"],
                                             data[e]["T_MOTS"],
                                             data[e]["T_LETTRES"])
            ts = data[e]["OLDEST_MSG"]
            date = "{}/{}/{} {}:{}".format(ts.day, ts.month, ts.year, ts.hour, ts.minute)
            data[e]["OLDEST_MSG"] = date
        filename = "StatsSS_{}".format(str(random.randint(1, 999)))
        file = open("data/outils/{}.txt".format(filename), "w", encoding="utf-8")
        file.write(txt)
        file.close()
        self.results[nom] = data
        fileIO("data/outils/results.json".format(filename), "save", self.results)
        try:
            await self.bot.send_file(ctx.message.channel, "data/outils/{}.txt".format(filename))
            os.remove("data/outils/{}.txt".format(filename))
        except:
            await self.bot.say("Impossible d'upload le fichier...")

def check_folders():
    if not os.path.exists("data/outils"):
        print("Creation du fichier Outils ...")
        os.makedirs("data/outils")

def check_files():
    if not os.path.isfile("data/outils/results.json"):
        print("Création de Outils/Results.json ...")
        fileIO("data/outils/results.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Outils(bot)
    bot.add_cog(n)
