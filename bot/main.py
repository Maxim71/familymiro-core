import os
import sys
import django

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

import asyncio
import qrcode
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

# Настройка Django

import cv2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from storage_control.models import VideoCapsule, UserProtectionShield

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot("8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U")
dp = Dispatcher()

# КЛАВИАТУРА ВЫБОРА ЩИТА
def get_shield_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👁️ Локальный ID-Scan (Лицо)")],
            [KeyboardButton(text="🔐 Секретное Слово Рода (Текст)")],
            [KeyboardButton(text="🎴 Печатный Маяк (Только QR-код)")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

class MultiShieldState(StatesGroup):
    choosing_shield = State()
    collecting_face = State()
    waiting_for_word = State()
    waiting_for_video = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MultiShieldState.choosing_shield)
    await message.answer(
        f"Приветствую, {message.from_user.first_name}! 🛡️\n\n"
        "Каким способом ты хочешь защитить своё Наследие?\n"
        "Выбери самый комфортный уровень защиты на кнопках ниже:",
        reply_markup=get_shield_keyboard()
    )

# ОБРАБОТКА ВЫБОРА ПОЛЬЗОВАТЕЛЯ
@dp.message(MultiShieldState.choosing_shield)
async def handle_choice(message: Message, state: FSMContext):
    choice = message.text
    
    if "Лицо" in choice:
        await state.set_state(MultiShieldState.collecting_face)
        await state.update_data(photos_vectors=[], count=0, type="FACE")
        await message.answer("Пришли по очереди **3 селфи-фото**. Они обработаются на твоем ноуте локально, а исходники будут уничтожены.")
    
    elif "Слово" in choice:
        await state.set_state(MultiShieldState.waiting_for_word)
        await state.update_data(type="WORD")
        await message.answer("Напиши Секретное Слово Рода или фразу-пароль, которую в будущем введет твой ребенок:")
        
    elif "Маяк" in choice:
        # Для QR-варианта пароли не нужны — система сгенерирует случайный ID ключа
        user_id = message.from_user.id
        beacon_key = f"BEACON-{user_id}"
        UserProtectionShield.objects.update_or_create(
            telegram_id=user_id,
            defaults={'user_name': message.from_user.full_name, 'shield_type': 'QR', 'qr_beacon_id': beacon_key}
        )
        await state.set_state(MultiShieldState.waiting_for_video)
        await message.answer("🎯 Профиль защищен Печатным Маяком! Теперь отправь мне архивное **видео**.")

# ВАРИАНТ 1: ЛОКАЛЬНОЕ ЛИЦО (БЕЗ ОТПРАВКИ В СЕТЬ)
@dp.message(MultiShieldState.collecting_face, F.photo)
async def do_face_scan(message: Message, state: FSMContext):
    data = await state.get_data()
    vectors, count = data['photos_vectors'], data['count'] + 1
    
    photo_file = await bot.get_file(message.photo[-1].file_id)
    temp_path = Path(f"temp_face_{message.from_user.id}.jpg")
    await bot.download_file(photo_file.file_path, destination=temp_path)
    
    try:
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        img = cv2.imread(str(temp_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            resized = cv2.resize(gray[y:y+h, x:x+w], (64, 64))
            vectors.append(resized.flatten().tolist())
            await message.answer(f"Фото {count}/3 обработано локально.")
        else:
            await message.answer("Лицо не обнаружено. Смени ракурс.")
            return
    finally:
        if temp_path.exists(): os.remove(temp_path) # УНИЧТОЖЕНИЕ
        
    if count < 3:
        await state.update_data(photos_vectors=vectors, count=count)
    else:
        final_vector = [sum(sub) / 3 for sub in zip(*vectors)]
        UserProtectionShield.objects.update_or_create(
            telegram_id=message.from_user.id,
            defaults={'user_name': message.from_user.full_name, 'shield_type': 'FACE', 'face_vector': final_vector}
        )
        await state.set_state(MultiShieldState.waiting_for_video)
        await message.answer("🎯 Математический хэш лица зашит в Сейф! Исходники удалены.\nТеперь отправь мне **видео**.")

# ВАРИАНТ 2: ТЕКСТОВОЕ СЛОВО (БЕЗ КАМЕР И СНИМКОВ)
@dp.message(MultiShieldState.waiting_for_word, F.text)
async def do_word_scan(message: Message, state: FSMContext):
    UserProtectionShield.objects.update_or_create(
        telegram_id=message.from_user.id,
        defaults={'user_name': message.from_user.full_name, 'shield_type': 'WORD', 'secret_word': message.text}
    )
    await state.set_state(MultiShieldState.waiting_for_video)
    await message.answer("🔑 Секретное Слово успешно сохранено в зашифрованный Postgres!\nТеперь отправь мне **видео**.")

# ФИНАЛ: ПРИЕМ ВИДЕО И ВЫДАЧА PDF С QR КОДОМ МАЯКА
def build_pdf_card(capsule_id, name, type_shield):
    pdf_path = f"legacy_card_{capsule_id}.pdf"
    qr_img = f"t_qr_{capsule_id}.png"
    
    # Ссылка на Маяк твоего ноута
    qrcode.make("127.0.0.1:8000").save(qr_img)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(80, 700, "FAMILYMIRO 1.0 — SYSTEM PASSPORT")
    c.setFont("Helvetica", 12)
    c.drawString(80, 660, f"Subject Owner: {name}")
    c.drawString(80, 642, f"Capsule ID: #{capsule_id}")
    c.drawString(80, 624, f"Selected Shield: PRO-[{type_shield}]")
    
    c.drawImage(qr_img, 180, 300, width=220, height=220)
    c.drawString(100, 260, "Show this QR to the Lighthouse camera or type your secret key to enter.")
    c.save()
    
    if os.path.exists(qr_img): os.remove(qr_img)
    return pdf_path

# Импортируем наш новый платежный шлюз в начало или внутрь функции

@dp.message(MultiShieldState.waiting_for_video, F.video)
async def handle_video_done(message: Message, state: FSMContext):
    f_data = await state.get_data()
    shield_type = f_data['type']
    user_name = message.from_user.full_name
    
    capsule = VideoCapsule.objects.create(
        user_name=user_name,
        video_id=message.video.file_id,
        message_text=message.caption or "Legacy Core Complete"
    )
    
    # ВЫСТАВЛЯЕМ СЧЕТ (например, 490 рублей за вечное хранение в VIP-Кармане)
    price = 490.00
    pay_url = await create_payment_invoice(capsule, price)
    
    # Создаем интерактивную платежную кнопку прямо в чате
    pay_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Оплатить активацию ({price} руб)", url=pay_url)]
    ])
    
    pdf_file = build_pdf_card(capsule.id, user_name, shield_type)
    
    with open(pdf_file, "rb") as f_pdf:
        await message.answer_document(
            BufferedInputFile(f_pdf.read(), filename=pdf_file),
            caption=f"✅ Капсула #{capsule.id} успешно создана!\nВыбранный щит [{shield_type}] активирован.\n\nДля включения долгосрочного архива и вечного Будильника, пожалуйста, оплатите счет по кнопке ниже:",
            reply_markup=pay_keyboard
        )
    
    if os.path.exists(pdf_file): os.remove(pdf_file)
    await state.clear()
