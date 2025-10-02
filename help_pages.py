import discord
from datetime import datetime
import pytz

# Link icon/footer (dùng hình bạn đưa)
ICON_URL = "https://i.imgur.com/TWW22k4.jpeg"
FOOTER_ICON_URL = "https://i.imgur.com/TWW22k4.jpeg"


def get_utc7_time():
    """Trả về thời gian hiện tại theo UTC+7 (Asia/Ho_Chi_Minh)."""
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(tz)


def build_help_pages(user_id: int, username: str, is_admin: bool = False):
    """Tạo ra 2 trang embed help"""

    current_time = get_utc7_time()

    # === PAGE 1 ===
    page1 = discord.Embed(
        title="🤖 Lonely Hub - Hệ Thống Lệnh (1/2)",
        description="📊 **Thông tin bot:**\n• Prefix: `!`, `?`, `.`, `/`\n• Múi giờ: `UTC+7`\n• Phiên bản: `1.0.0`",
        color=0x00ffaa,
        timestamp=current_time
    )
    page1.add_field(
        name="🔧 LỆNH CƠ BẢN",
        value=(
            "• `/ping`\n"
            "• `/info`\n"
            "• `/whitelist`\n"
            "• `/help`\n"
            "• `/say`, `/sayv2`\n"
            "• `/ghostping`, `/ghostpingv2`\n"
            "• `/dms`\n"
            "• `/spam`, `/spamv2`\n"
            "• `/invite`"
        ),
        inline=False
    )
    page1.add_field(
        name="💰 ECONOMY & CASINO",
        value=(
            "• `/balance`, `/daily`, `/work`\n"
            "• `/shop`, `/buy`\n"
            "• `/gamble`, `/guess`, `/slot`\n"
            "• `/taixiu`, `/lichsutaixiu`"
        ),
        inline=False
    )
    page1.add_field(
        name="🏆 LEVEL & RANK",
        value="• `/rank`\n• `/leaderboard`\n• `/tag`, `/reset-tag`",
        inline=False
    )
    page1.add_field(
        name="📦 MYSTERY BOX",
        value="• `/box`, `/boxopen`",
        inline=False
    )
    page1.add_field(
        name="🎫 TICKET SYSTEM",
        value="• `/setup`, `/setup-list`, `/ticket`",
        inline=False
    )
    page1.set_thumbnail(url=ICON_URL)
    page1.set_footer(text=f"Yêu cầu bởi {username} | Trang 1/2", icon_url=FOOTER_ICON_URL)

    # === PAGE 2 ===
    page2 = discord.Embed(
        title="🤖 Lonely Hub - Hệ Thống Lệnh (2/2)",
        color=0x00ffaa,
        timestamp=current_time
    )
    page2.add_field(
        name="🏷️ TAG SYSTEM (Admin)",
        value="• `/tag-list`, `/add-tag`, `/remove-tag`, `/give-tag`, `/remove-user-tag`",
        inline=False
    )
    page2.add_field(
        name="🎵 MUSIC",
        value="• `/join`, `/leave`, `/play`, `/stop`, `/pause`, `/resume`",
        inline=False
    )
    page2.add_field(
        name="🔧 UTILITY",
        value="• `/serverinfo`, `/userinfo`, `/premium`, `/script`, `/time`",
        inline=False
    )

    if is_admin:
        page2.add_field(
            name="⚡ LỆNH ADMIN",
            value=(
                "• `/premium_command`\n"
                "• `/bancmd`, `/unbancmd`, `/bancmdlist`\n"
                "• `/addwhitelist`, `/removewhitelist`\n"
                "• `/addcoin`, `/removecoin`, `/setcoin`\n"
                "• `/addbox`, `/removebox`, `/setbox`"
            ),
            inline=False
        )
        page2.add_field(
            name="💎 TEXT COMMANDS PREMIUM",
            value="`?nukeall`, `?raidall`, `?spampingall`, `?banalluser`, `?purge`, `?purgeallwebhook`",
            inline=False
        )
    else:
        page2.add_field(
            name="🔒 ADMIN / PREMIUM",
            value="*Bạn không có quyền sử dụng các lệnh này*",
            inline=False
        )

    page2.add_field(
        name="🤖 AUTO RESPONSE",
        value="`client`, `executor`, `luật`, `máy ảo`...",
        inline=False
    )
    page2.add_field(
        name="📝 NOTES",
        value="• Admin commands chỉ cho user được cấp quyền\n• Tất cả lệnh được log + DM Owner\n• Múi giờ: UTC+7\n• Prefix: ! ? . /",
        inline=False
    )
    page2.set_thumbnail(url=ICON_URL)
    page2.set_footer(text=f"Yêu cầu bởi {username} | Trang 2/2", icon_url=FOOTER_ICON_URL)

    return [page1, page2]


class HelpView(discord.ui.View):
    """View có nút phân trang cho help"""
    def __init__(self, pages, author_id):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Không phải của bạn!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="⏮️ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="⏭️ Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.red)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()