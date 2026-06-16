# ─────────────────────────────────────────────
#  main.py  —  Telegram bot  (aiogram v3)
#
#  Run:  python main.py
# ─────────────────────────────────────────────

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import BOT_TOKEN
from database import get_conn, init_db
from engine import add_report, find_nearest_spots

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())


# ── i18n ─────────────────────────────────────────────────────────────

def _detect_lang_code(language_code: str | None) -> str:
    if not language_code:
        return "ru"
    lc = language_code.lower()
    if lc.startswith("en"):
        return "en"
    if lc.startswith("ru"):
        return "ru"
    return "ru"


def get_user_lang(user_id: int, telegram_language_code: str | None) -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT lang FROM user_settings WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    if row is not None:
        lang = row["lang"]
        conn.close()
        return lang

    lang = _detect_lang_code(telegram_language_code)
    conn.execute(
        "INSERT OR IGNORE INTO user_settings (user_id, lang) VALUES (?, ?)",
        (user_id, lang),
    )
    conn.commit()
    conn.close()
    return lang


T: dict[str, dict[str, str]] = {
    "en": {
        "share_location": "📍 Share my location",
        "address_prompt": "🏙️ Enter an address or place name:",
        "address_placeholder": "e.g. Independence Ave 10, Minsk",
        "start": (
            "🅿️ *Free Parking Finder*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "I find the nearest *free* parking spots using OpenStreetMap + live crowd reports.\n\n"
            "Use location search or type an address.\n\n"
            "/help — how it works\n"
            "/stats — database stats"
        ),
        "help": (
            "*How it works*\n\n"
            "1️⃣  Use *location* or type an *address*.\n"
            "2️⃣  I search for free/likely-free spots within *{radius_km} km*.\n"
            "3️⃣  Each spot gets a live pin on the map.\n"
            "4️⃣  After visiting, tap ✅ *Still free* or 🔴 *Full/taken* so other drivers know.\n\n"
            "*Status colours*\n"
            "🟢 Likely free\n"
            "🟡 Mixed reports — approach with caution\n"
            "🔴 Confirmed full — hidden from results\n\n"
            "⚠️  *Courtyard spots* are legal grey areas. Always check for barriers (шлагбаум) before driving in."
        ),
        "find": "📍 Share your location and I'll search nearby:",
        "address_button": "⌨️ Search by address",
        "stats": "📊 *Database stats*",
        "searching": "🔍 Searching …",
        "no_spots": (
            "😕 No free spots found within {radius_km} km.\n\n"
            "Possible reasons:\n"
            "• The database hasn't been seeded yet — run `python osm_fetcher.py` first.\n"
            "• All nearby spots have been reported as full.\n"
            "• This area isn't in the database yet (seed it in `osm_fetcher.py`)."
        ),
        "header": "🅿️ *{count} free spot(s)* found nearby:\n\n",
        "arrival_question": "📍 *{name}* — was this spot free when you arrived?",
        "report_free": "✅ Marked as *free* — thank you!",
        "report_full": "🔴 Marked as *full* — thank you!",
        "lang_choose": "Choose language:",
        "lang_set_en": "English",
        "lang_set_ru": "Русский",
        "courtyard_warning": "⚠️  *Courtyard spots* — legal grey areas. Always check for barriers before driving in.",
        "low_cert_barrier": "⚠️ _Low certainty — check for barriers_",
        "stats_by_city": "By city:",
        "stats_by_type": "By type:",
    },
    "ru": {
        "share_location": "📍 Отправить местоположение",
        "address_prompt": "🏙️ Введите адрес или название места:",
        "address_placeholder": "например, проспект Независимости 10, Минск",
        "start": (
            "🅿️ *Бесплатная парковка Finder*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Я нахожу ближайшие *свободные* места для парковки по данным OpenStreetMap и живым сообщениям от водителей.\n\n"
            "Используйте поиск по локации или введите адрес.\n\n"
            "/help — как это работает\n"
            "/stats — статистика базы"
        ),
        "help": (
            "*Как это работает*\n\n"
            "1️⃣  Используйте *локацию* или введите *адрес*.\n"
            "2️⃣  Я найду свободные/скорее свободные места в радиусе *{radius_km} км*.\n"
            "3️⃣  Для каждого места будет отправлена отметка на карте.\n"
            "4️⃣  Когда приедете — нажмите ✅ *По-прежнему свободно* или 🔴 *Занято/полно*, чтобы другим водителям было проще.\n\n"
            "*Цвета статуса*\n"
            "🟢 Скорее свободно\n"
            "🟡 Смешанные сообщения — лучше подъезжать с осторожностью\n"
            "🔴 Подтверждено занято — скрыто из результатов\n\n"
            "⚠️  *Дворовые места* — юридически серая зона. Всегда проверяйте шлагбаум перед въездом."
        ),
        "find": "📍 Отправьте локацию — и я найду места рядом:",
        "address_button": "⌨️ Поиск по адресу",
        "stats": "📊 *Статистика базы*",
        "searching": "🔍 Ищу …",
        "no_spots": (
            "😕 Не найдено свободных мест в радиусе {radius_km} км.\n\n"
            "Возможные причины:\n"
            "• База ещё не заполнена — выполните `python osm_fetcher.py` сначала.\n"
            "• Рядом все места уже помечены как занятые.\n"
            "• Эта территория ещё не добавлена в базу (засейте её в `osm_fetcher.py`)."
        ),
        "header": "🅿️ *Найдено {count} свободных места(мест)* рядом:\n\n",
        "arrival_question": "📍 *{name}* — было свободно, когда вы подъехали?",
        "report_free": "✅ Отмечено как *свободно* — спасибо!",
        "report_full": "🔴 Отмечено как *занято* — спасибо!",
        "lang_choose": "Выберите язык:",
        "lang_set_en": "English",
        "lang_set_ru": "Русский",
        "courtyard_warning": "⚠️  *Дворовые места* — юридически серая зона. Всегда проверяйте шлагбаум перед въездом.",
        "low_cert_barrier": "⚠️ _Низкая достоверность — проверьте шлагбаум_",
        "stats_by_city": "По городам:",
        "stats_by_type": "По типам:",
        "address_placeholder": "например, проспект Независимости 10, Минск",
        "address_button": "⌨️ Поиск по адресу",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    return T[lang][key].format(**kwargs)


# ── Keyboards ─────────────────────────────────────────────────────────────

def kb_main(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=T[lang]["share_location"], request_location=True)],
            [KeyboardButton(text=T[lang]["address_button"], request_location=False)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def kb_report(lang: str, spot_id: int) -> InlineKeyboardMarkup:
    if lang == "ru":
        free_txt = "✅ По-прежнему свободно"
        full_txt = "🔴 Занято/полно"
    else:
        free_txt = "✅ Still free"
        full_txt = "🔴 Full / taken"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=free_txt, callback_data=f"report:free:{spot_id}"),
                InlineKeyboardButton(text=full_txt, callback_data=f"report:full:{spot_id}"),
            ]
        ]
    )


def kb_lang_select(lang: str) -> InlineKeyboardMarkup:
    # lang is unused except future highlighting; keep signature stable
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=T["en"]["lang_set_en"], callback_data="lang:set:en"),
                InlineKeyboardButton(text=T["ru"]["lang_set_ru"], callback_data="lang:set:ru"),
            ]
        ]
    )


# ── Formatters ─────────────────────────────────────────────────────────────

STATUS_EMOJI = {"free": "🟢", "likely_full": "🟡", "full": "🔴"}

TYPE_LABEL = {
    "street": {"en": "Street parking", "ru": "Уличная парковка"},
    "courtyard": {"en": "Courtyard", "ru": "Двор"},
    "lot": {"en": "Parking lot", "ru": "Паркинг"},
}


def fmt_spot(rank: int, spot: dict, lang: str) -> str:
    emoji = STATUS_EMOJI.get(spot["status"], "🟢")

    kind = TYPE_LABEL.get(spot["spot_type"], {}).get(lang)
    if not kind:
        kind = spot["spot_type"]

    name = spot["name"] if spot["name"] and spot["name"] != "Unnamed spot" else kind

    dist = spot["distance_m"]
    cap = f" · {spot['capacity']} spaces" if spot["capacity"] else ""
    rpts = f" · {spot['reports']} report(s)" if spot["reports"] else ""

    if lang == "ru":
        cap = f" · {spot['capacity']} мест" if spot["capacity"] else ""
        rpts = f" · {spot['reports']} отчёт(ов)" if spot["reports"] else ""

    warn = ("\n   " + t(lang, "low_cert_barrier")) if spot["certainty"] == "low" else ""

    if lang == "ru":
        return (
            f"{rank}. {emoji} *{name}*\n"
            f"   📏 {dist} м до  |  {kind}{cap}{rpts}{warn}"
        )

    return (
        f"{rank}. {emoji} *{name}*\n"
        f"   📏 {dist} m away  |  {kind}{cap}{rpts}{warn}"
    )


# ── Search by coordinates helper ──────────────────────────────────────────

from config import MAX_RESULTS, SEARCH_RADIUS_KM  # noqa: E402


async def send_results(chat_id: int, user_id: int, lat: float, lon: float, lang: str) -> None:
    await bot.send_message(chat_id=chat_id, text=t(lang, "searching"), reply_markup=ReplyKeyboardRemove())

    spots = find_nearest_spots(lat, lon, limit=MAX_RESULTS)

    if not spots:
        await bot.send_message(
            chat_id=chat_id,
            text=t(lang, "no_spots", radius_km=SEARCH_RADIUS_KM),
        )
        return

    header = t(lang, "header", count=len(spots))
    summary = "\n\n".join(fmt_spot(i + 1, s, lang) for i, s in enumerate(spots))
    await bot.send_message(chat_id=chat_id, text=header + summary)

    for spot in spots:
        await bot.send_location(chat_id=chat_id, latitude=spot["lat"], longitude=spot["lon"])
        await bot.send_message(
            chat_id=chat_id,
            text=t(lang, "arrival_question", name=spot["name"] if spot["name"] else ""),
            reply_markup=kb_report(lang, spot["id"]),
        )


# ── Command handlers ─────────────────────────────────────────────────────────────


@dp.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    lang = get_user_lang(msg.from_user.id, msg.from_user.language_code)
    await msg.answer(t(lang, "start"), reply_markup=kb_main(lang))


@dp.message(Command("help"))
async def cmd_help(msg: Message) -> None:
    lang = get_user_lang(msg.from_user.id, msg.from_user.language_code)
    await msg.answer(t(lang, "help", radius_km=SEARCH_RADIUS_KM), reply_markup=kb_main(lang))


@dp.message(Command("lang"))
async def cmd_lang(msg: Message) -> None:
    lang = get_user_lang(msg.from_user.id, msg.from_user.language_code)
    await msg.answer(t(lang, "lang_choose"), reply_markup=kb_lang_select(lang))


@dp.message(Command("find"))
async def cmd_find(msg: Message) -> None:
    lang = get_user_lang(msg.from_user.id, msg.from_user.language_code)
    await msg.answer(t(lang, "find"), reply_markup=kb_main(lang))


@dp.message(Command("stats"))
async def cmd_stats(msg: Message) -> None:
    from database import get_conn

    lang = get_user_lang(msg.from_user.id, msg.from_user.language_code)
    conn = get_conn()

    total = conn.execute("SELECT COUNT(*) FROM spots").fetchone()[0]
    by_city = conn.execute("SELECT city, COUNT(*) FROM spots GROUP BY city").fetchall()
    by_type = conn.execute("SELECT spot_type, COUNT(*) FROM spots GROUP BY spot_type").fetchall()
    reports = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    conn.close()

    city_lines = "\n".join(f"  • {r[0] or 'unknown'}: {r[1]}" for r in by_city)
    type_lines = "\n".join(f"  • {r[0]}: {r[1]}" for r in by_type)

    await msg.answer(
        f"{t(lang, 'stats')}\n\n"
        f"Total spots: *{total}*\n\n"
        f"{t(lang, 'stats_by_city')}\n{city_lines}\n\n"
        f"{t(lang, 'stats_by_type')}\n{type_lines}\n\n"
        f"Total crowd reports: *{reports}*"
    )


# ── Location search ─────────────────────────────────────────────────────────────

@dp.message(F.location)
async def handle_location(msg: Message) -> None:
    lang = get_user_lang(msg.from_user.id, msg.from_user.language_code)
    await send_results(
        chat_id=msg.chat.id,
        user_id=msg.from_user.id,
        lat=msg.location.latitude,
        lon=msg.location.longitude,
        lang=lang,
    )


# Address flow (simple):
# 1) user presses "Search by address" button (language-specific)
# 2) we ask for text
# 3) next plain text message is treated as address (no external state, just per-user in-memory memory)

ADDRESS_STATE: dict[int, bool] = {}


@dp.message(F.text)
async def handle_text(msg: Message) -> None:
    lang = get_user_lang(msg.from_user.id, msg.from_user.language_code)

    if msg.text == T[lang]["address_button"]:
        ADDRESS_STATE[msg.from_user.id] = True
        await msg.answer(t(lang, "address_prompt"), reply_markup=ReplyKeyboardRemove())
        return

    if ADDRESS_STATE.get(msg.from_user.id):
        # geocode address -> coordinates using OpenStreetMap Nominatim
        query = msg.text.strip()
        ADDRESS_STATE[msg.from_user.id] = False

        await msg.answer(t(lang, "searching"), reply_markup=ReplyKeyboardRemove())

        try:
            import requests

            resp = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 0,
                },
                headers={"User-Agent": "FreeParkingBot/1.0"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            if not data:
                await msg.answer(t(lang, "no_spots", radius_km=SEARCH_RADIUS_KM))
                return
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])

            await send_results(
                chat_id=msg.chat.id,
                user_id=msg.from_user.id,
                lat=lat,
                lon=lon,
                lang=lang,
            )
        except Exception:
            await msg.answer(t(lang, "no_spots", radius_km=SEARCH_RADIUS_KM))


# ── Callback: language selection ───────────────────────────────────────────────

@dp.callback_query(F.data.startswith("lang:set:"))
async def handle_lang_set(cb: CallbackQuery) -> None:
    _, _, lang = cb.data.split(":", 2)
    lang = "ru" if lang == "ru" else "en"

    conn = get_conn()
    conn.execute(
        "INSERT INTO user_settings (user_id, lang) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang",
        (cb.from_user.id, lang),
    )
    conn.commit()
    conn.close()

    await cb.answer()
    await cb.message.edit_reply_markup(reply_markup=None)


# ── Callback: crowd report ───────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("report:"))
async def handle_report(cb: CallbackQuery) -> None:
    _, status, spot_id_str = cb.data.split(":")
    spot_id = int(spot_id_str)

    # language for popup
    lang = get_user_lang(cb.from_user.id, cb.from_user.language_code)

    add_report(spot_id, cb.from_user.id, status)

    reply = t(lang, "report_free") if status == "free" else t(lang, "report_full")

    await cb.answer(reply)
    await cb.message.edit_reply_markup(reply_markup=None)


# ── Entry point ─────────────────────────────────────────────────────────────


async def main() -> None:
    init_db()
    logging.info("Bot starting — polling …")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())

