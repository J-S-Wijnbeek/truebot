"""Tests voor de onderdelen die zonder Discord-verbinding werken: python -m unittest"""

import unittest

import bot


class Helpers(unittest.TestCase):
    def test_is_translatable(self):
        self.assertTrue(bot.is_translatable("Привет всем!"))
        self.assertTrue(bot.is_translatable("look at this https://example.com"))
        for text in ("https://example.com/a", "😂😂 <:kek:123>", "<@123> 42", "```py\nx = 1\n```", "@everyone"):
            self.assertFalse(bot.is_translatable(text), text)

    def test_excerpt(self):
        self.assertEqual(bot.excerpt("een\ntwee   drie"), "een twee drie")
        self.assertEqual(len(bot.excerpt("a" * 200)), 80)
        self.assertEqual(bot.excerpt(""), "📎")

    def test_safe_username(self):
        self.assertNotIn("discord", bot.safe_username("Discord Fan").lower())
        self.assertEqual(len(bot.safe_username("x" * 100)), 80)
        self.assertEqual(bot.safe_username("  "), "?")

    def test_reaction_line(self):
        rows = [
            {"channel_id": 1, "emoji": "👍", "user_name": "Ivan"},
            {"channel_id": 1, "emoji": "👍", "user_name": "Olga"},
            {"channel_id": 1, "emoji": "😂", "user_name": "Dmitri"},
            {"channel_id": 2, "emoji": "❤️", "user_name": "John"},
        ]
        self.assertEqual(bot.reaction_line(rows, 2), "-# 👍 Ivan, Olga · 😂 Dmitri")
        self.assertEqual(bot.reaction_line(rows, 1), "-# ❤️ John")
        self.assertEqual(bot.reaction_line([], 1), "")

    def test_compose(self):
        self.assertEqual(bot.compose("", "hoi", "", ""), "hoi")
        self.assertEqual(bot.compose("> ↩ a", "hoi", "http://x", "-# 👍 b"), "> ↩ a\nhoi\nhttp://x\n-# 👍 b")
        long = bot.compose("> ↩ citaat", "a" * 5000, "", "-# 👍 Ivan")
        self.assertLessEqual(len(long), 2000)
        self.assertTrue(long.startswith("> ↩ citaat"))
        self.assertTrue(long.endswith("-# 👍 Ivan"))

    def test_strip_decorations(self):
        self.assertEqual(bot.strip_decorations("> ↩ **A** hoi\nde tekst\n-# 👍 B"), "de tekst")

    def test_parse_channels(self):
        self.assertEqual(bot.parse_channels("en:123, RU:456,fout,x:abc"), {"en": 123, "ru": 456})
        self.assertEqual(bot.parse_channels(""), {})

    def test_language_of_channel(self):
        config = {"languages": {"ru": {"channel_id": 10}, "en": {"channel_id": 20}}}
        self.assertEqual(bot.language_of_channel(config, 20), "en")
        self.assertIsNone(bot.language_of_channel(config, 30))


class Limiter(unittest.TestCase):
    def test_per_minute(self):
        now = [1000.0]
        limiter = bot.RateLimiter(2, 100, clock=lambda: now[0])
        self.assertIsNone(limiter.allow(1))
        self.assertIsNone(limiter.allow(1))
        self.assertEqual(limiter.allow(1), "minuutlimiet")
        self.assertIsNone(limiter.allow(2))  # andere gebruiker heeft eigen limiet
        now[0] += 61
        self.assertIsNone(limiter.allow(1))

    def test_daily_budget(self):
        now = [1000.0]
        limiter = bot.RateLimiter(100, 1.0, clock=lambda: now[0])
        self.assertIsNone(limiter.allow(1))
        self.assertEqual(limiter.add_cost(0.4), [])
        self.assertEqual(limiter.add_cost(0.2), [50])
        self.assertEqual(limiter.add_cost(0.1), [])
        self.assertIsNone(limiter.allow(2))
        self.assertEqual(limiter.add_cost(0.4), [80, 100])
        self.assertEqual(limiter.allow(3), "dagbudget op")
        now[0] += 86400
        self.assertIsNone(limiter.allow(3))
        self.assertEqual(limiter.spent, 0.0)


class Storage(unittest.TestCase):
    def setUp(self):
        self.store = bot.Store(":memory:")

    def test_guild_config_roundtrip(self):
        config = self.store.guild(1)
        self.assertEqual(config, {"languages": {}, "log_level": "alles"})
        config["languages"]["ru"] = {"name": "Russisch", "flag": "🇷🇺", "channel_id": 5}
        self.store.save_guild(1)
        self.store._guilds.clear()
        self.assertEqual(self.store.guild(1)["languages"]["ru"]["channel_id"], 5)

    def test_message_groups(self):
        self.store.add_origin(100, 1, 7, "Ivan")
        self.store.add_copy(100, 100, 10, body="Привет")
        self.store.add_copy(200, 100, 20, "", "Hello", "")
        self.assertEqual(self.store.copy(200)["origin_id"], 100)
        self.assertEqual(len(self.store.copies_of(100)), 2)
        self.store.update_body(200, "Hi")
        self.assertEqual(self.store.copy(200)["body"], "Hi")

        self.store.add_reaction(100, 10, 7, "👍", "Ivan")
        self.store.add_reaction(100, 10, 8, "👍", "Olga")
        self.assertEqual(bot.reaction_line(self.store.reactions(100), 20), "-# 👍 Ivan, Olga")
        self.store.remove_reactions(100, 10, 7, "👍")
        self.assertEqual(bot.reaction_line(self.store.reactions(100), 20), "-# 👍 Olga")

        self.store.delete_group(100)
        self.assertIsNone(self.store.copy(200))
        self.assertEqual(self.store.reactions(100), [])

    def test_spend(self):
        self.assertEqual(self.store.spent(5), 0.0)
        self.store.add_spend(5, 0.25)
        self.store.add_spend(5, 0.5)
        self.assertEqual(self.store.spent(5), 0.75)
        self.assertEqual(self.store.spent(6), 0.0)

    def test_prune(self):
        self.store.add_origin(1, 1, 1, "A")
        self.store.add_copy(1, 1, 10, body="oud")
        self.store.db.execute("UPDATE origins SET created_at = 0")
        self.store.add_origin(2, 1, 1, "A")
        self.store.add_copy(2, 2, 10, body="nieuw")
        self.store.prune(30)
        self.assertIsNone(self.store.copy(1))
        self.assertIsNotNone(self.store.copy(2))


class Client(unittest.IsolatedAsyncioTestCase):
    async def test_commands_registered(self):
        client = bot.Vertaalbot(bot.Store(":memory:"), anthropic=None, model="test")
        names = sorted(command.name for command in client.tree.get_commands())
        self.assertEqual(names, ["log", "setup", "taal-toevoegen"])
        view = client.language_view({"languages": bot.DEFAULT_LANGUAGES})
        self.assertEqual([item.custom_id for item in view.children],
                         ["vertaalbot:taal:ru", "vertaalbot:taal:en"])

        # Kosten worden uit het tokengebruik berekend en overleven een herstart.
        from types import SimpleNamespace as NS
        from unittest.mock import AsyncMock
        response = NS(content=[NS(type="text", text="Hello")],
                      usage=NS(input_tokens=1_000_000, output_tokens=1_000_000))
        client.anthropic = NS(messages=NS(create=AsyncMock(return_value=response)))
        self.assertEqual(await client.translate("Привет", "Russisch", "Engels", "Ivan", []), "Hello")
        self.assertAlmostEqual(client.limiter.spent, 0.60)
        self.assertEqual(client.budget_alerts, [50])
        sent = []
        async def audit(guild, title, text="", important=False):
            sent.append(title)
        client.audit = audit
        await client.report_budget(None)
        self.assertEqual(sent, ["⚠️ 50% van het dagbudget gebruikt"])
        self.assertEqual(client.budget_alerts, [])
        self.assertEqual(client.limiter.allow(1), None)
        await client.translate("Привет", "Russisch", "Engels", "Ivan", [])
        self.assertEqual(client.limiter.allow(1), "dagbudget op")
        restarted = bot.Vertaalbot(client.store, anthropic=None, model="test")
        self.assertAlmostEqual(restarted.limiter.spent, 1.20)
        await restarted.close()
        await client.close()


if __name__ == "__main__":
    unittest.main()
