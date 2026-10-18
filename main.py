from telegram import Update,BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TOKEN, ADMIN_ID
from database import (
    create_database,
    find_customer,
    save_customer,
    update_customer,
    change_status,
    get_all_customers,
    save_message,
    get_messages
)

ALLOWED_STATUS = [
    "New",
    "Contacted",
    "In Progress",
    "Closed",
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome!\n\n"
        "This is a simple Customer Management System.\n"
        "Please send your message, and your information will be saved for follow-up.\n\n"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    telegram_id = user.id
    first_name = user.first_name
    username = user.username or "No Username"
    message = update.message.text
    save_message(telegram_id, message)

    customer = find_customer(telegram_id)

    if customer is None:
        save_customer(
            telegram_id,
            first_name,
            username,
            message,
        )

        await update.message.reply_text(
            "Your information has been successfully registered.\n"
            "Our team will contact you as soon as possible."
        )

    else:
        update_customer(
            telegram_id,
            first_name,
            username,
            message,
        )

        await update.message.reply_text(
            "Your information has been successfully updated."
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage:\n/status <telegram_id> <status>"
        )
        return

    telegram_id = int(context.args[0])
    new_status = " ".join(context.args[1:])

    if new_status not in ALLOWED_STATUS:
        await update.message.reply_text(
            "Invalid status.\n"
            "Available values:\n"
            "New\n"
            "Contacted\n"
            "In Progress\n"
            "Closed"
        )
        return

    change_status(telegram_id, new_status)

    await update.message.reply_text(
        f"Status updated to: {new_status}"
    )
    
async def customers(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    customers = get_all_customers()

    if not customers:
        await update.message.reply_text("No customers found.")
        return

    message = "Customers List:\n\n"

    for i, c in enumerate(customers, start=1):
        telegram_id, first_name, username, last_message, status, updated_at = c

        message += (
            f"{i}.\n"
            f"Telegram ID: {telegram_id}\n"
            f"Name: {first_name}\n"
            f"Username: {username}\n"
            f"Status: {status}\n"
            f"Last Message: {last_message}\n"
            f"Updated: {updated_at}\n\n"
        )

    await update.message.reply_text(message)
    
    
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "Usage:\n/history <telegram_id>"
        )
        return

    telegram_id = int(context.args[0])

    messages = get_messages(telegram_id)

    if not messages:
        await update.message.reply_text(
            "No messages found."
        )
        return

    text = "Message History\n\n"

    for i, (message, created_at) in enumerate(messages, start=1):
        text += (
            f"{i}.\n"
            f"Date: {created_at}\n"
            f"Message: {message}\n\n"
        )

    await update.message.reply_text(text)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("customers", "Show all customers"),
        BotCommand("history", "Show customer message history"),
        BotCommand("status", "Update customer status"),
    ])

create_database()

app = (
    Application.builder()
    .token(TOKEN)
    .post_init(post_init)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message,
    )
)
app.add_handler(CommandHandler("customers", customers))
app.add_handler(CommandHandler("history", history))

print("Bot is running...")
app.run_polling()